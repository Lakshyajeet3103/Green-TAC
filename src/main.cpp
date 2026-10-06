#include "greentac/lexer.h"
#include "greentac/parser.h"
#include "greentac/tac.h"
#include "greentac/optimizer.h"
#include "greentac/features.h"
#include "greentac/selector.h"
#include "greentac/codegen_c.h"
#include "greentac/energy.h"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <string>
#include <cstdlib>
#include <cmath>

using namespace greentac;

static std::string readFile(const std::string& p){
    std::ifstream in(p);
    if(!in) throw std::runtime_error("Cannot open "+p);
    return std::string((std::istreambuf_iterator<char>(in)),{});
}

static std::string num(double x, int p=3){
    std::ostringstream os; os<<std::fixed<<std::setprecision(p)<<x; return os.str();
}

static void usage(){
    std::cout << R"(
Green TAC — Carbon-Aware Adaptive TAC Optimizer

USAGE
  green_tac tac <file> <baseline|lightweight|dag>
  green_tac compare <file>
  green_tac features <file>
  green_tac c <file> <baseline|lightweight|dag> <out.c>
  green_tac select <file> [model.csv] [compileCI] [runtimeCI] [executions] [maxRuntimeOverhead]
  green_tac info
  green_tac energy-check
  green_tac demo [file]

Examples
  green_tac compare benchmarks/cse.c
  green_tac tac benchmarks/cse.c dag
  green_tac select benchmarks/cse.c data/model.csv 700 200 10000 0.10
  green_tac c benchmarks/cse.c dag output.c

Notes
  Energy values are measured only when a supported provider is available.
  Otherwise the selector uses a clearly labeled proxy model for demonstration.
)";
}

static Strategy parseStrategy(const std::string& x){
    if(x=="baseline")return Strategy::Baseline;
    if(x=="lightweight")return Strategy::Lightweight;
    if(x=="dag")return Strategy::DAG;
    throw std::runtime_error("Unknown strategy: "+x);
}

static TACProgram parseProgram(const std::string& path){
    return TACGenerator().generate(Parser(Lexer(readFile(path)).lex()).parse());
}

static void printFeatureSummary(const Features& f){
    std::cout << "  Instructions          " << std::setw(6) << static_cast<int>(f.instructions) << "\n";
    std::cout << "  Binary operations      " << std::setw(6) << static_cast<int>(f.binary_ops) << "\n";
    std::cout << "  Branches               " << std::setw(6) << static_cast<int>(f.branches) << "\n";
    std::cout << "  Labels                 " << std::setw(6) << static_cast<int>(f.labels) << "\n";
    std::cout << "  Temporaries            " << std::setw(6) << static_cast<int>(f.temporaries) << "\n";
    std::cout << "  Basic blocks           " << std::setw(6) << static_cast<int>(f.basic_blocks) << "\n";
    std::cout << "  Expression depth       " << std::setw(6) << static_cast<int>(f.max_expr_depth) << "\n";
    std::cout << "  Common subexpressions  " << std::setw(6) << static_cast<int>(f.common_subexpressions) << "\n";
}

static void printStrategyTable(const TACProgram& base){
    std::cout << "\n┌────────────────┬────────────┬────────────┬────────────┬─────────────┐\n";
    std::cout << "│ Strategy       │ TAC instr. │ Temporaries│ CSEs       │ Binaries    │\n";
    std::cout << "├────────────────┼────────────┼────────────┼────────────┼─────────────┤\n";
    for(Strategy s:{Strategy::Baseline,Strategy::Lightweight,Strategy::DAG}){
        auto t=optimize(base,s); auto f=extractFeatures(t);
        std::cout << "│ "<<std::left<<std::setw(14)<<strategyName(s)<<" │ "
                  <<std::right<<std::setw(10)<<static_cast<int>(f.instructions)<<" │ "
                  <<std::setw(10)<<static_cast<int>(f.temporaries)<<" │ "
                  <<std::setw(10)<<static_cast<int>(f.common_subexpressions)<<" │ "
                  <<std::setw(11)<<static_cast<int>(f.binary_ops)<<" │\n";
    }
    std::cout << "└────────────────┴────────────┴────────────┴────────────┴─────────────┘\n";
    auto bf=extractFeatures(optimize(base,Strategy::Baseline));
    auto df=extractFeatures(optimize(base,Strategy::DAG));
    if(bf.instructions>0){
        double save=(1.0-df.instructions/bf.instructions)*100.0;
        std::cout << "\nDAG TAC instruction change: " << num(save,1) << "% versus baseline\n";
    }
}

static void printTACWithHeader(const TACProgram& t){
    std::cout << "-------------------------------- TAC --------------------------------\n";
    t.print(std::cout);
    std::cout << "------------------------------------------------------------------------\n";
}

static int commandSelect(const TACProgram& base, const std::string& modelPath, double compileCI, double runtimeCI, double executions, double maxOverhead){
    Model m=loadModel(modelPath);
    Features f=extractFeatures(base);
    CarbonScenario cs; cs.compileCI_g_per_kWh=compileCI; cs.runtimeCI_g_per_kWh=runtimeCI; cs.expectedExecutions=executions;
    SelectionConfig cfg{cs,maxOverhead};
    auto sr=selectStrategy(base,f,m,cfg);

    std::cout << "\n================ GREEN STRATEGY DECISION ================\n";
    std::cout << "Model                 : " << (m.fullyCalibrated?"fully calibrated":"partial / proxy fallback") << "\n";
    std::cout << "Compile-energy model  : " << (m.hasCompileEnergy?"yes":"no") << "\n";
    std::cout << "Runtime-energy model  : " << (m.hasRuntimeEnergy?"yes":"no") << "\n";
    std::cout << "Runtime-time model    : " << (m.hasRuntimeMs?"yes":"no") << "\n";
    std::cout << "Compile carbon        : " << num(compileCI,1) << " gCO2e/kWh\n";
    std::cout << "Runtime carbon        : " << num(runtimeCI,1) << " gCO2e/kWh\n";
    std::cout << "Expected executions   : " << num(executions,0) << "\n";
    std::cout << "Max runtime overhead  : " << num(maxOverhead*100.0,1) << "%\n\n";
    printFeatureSummary(f);

    std::cout << "\n┌────────────────┬────────────┬────────────┬────────────┬──────────────┐\n";
    std::cout << "│ Strategy       │ Compile J  │ Runtime J  │ Runtime ms │ CO2e (g)     │\n";
    std::cout << "├────────────────┼────────────┼────────────┼────────────┼──────────────┤\n";
    for(const auto& c:sr.candidates){
        std::cout << "│ "<<std::left<<std::setw(14)<<strategyName(c.strategy)<<" │ "
                  <<std::right<<std::setw(10)<<num(c.compileEnergyJ)<<" │ "
                  <<std::setw(10)<<num(c.runtimeEnergyJ)<<" │ "
                  <<std::setw(10)<<num(c.runtimeMs)<<" │ "
                  <<std::setw(12)<<num(c.carbonGrams,6)<<" │\n";
    }
    std::cout << "└────────────────┴────────────┴────────────┴────────────┴──────────────┘\n";
    std::cout << "\nSelected strategy    : " << strategyName(sr.selected) << "\n";
    if(!m.hasCompileEnergy || !m.hasRuntimeEnergy) std::cout << "Measurement note      : at least one energy model is unavailable; proxy estimates are used for missing metrics.\n";
    std::cout << "=========================================================\n";
    printTACWithHeader(optimize(base,sr.selected));
    return 0;
}

int main(int argc,char**argv){
    try{
        if(argc<2){usage();return 2;}
        std::string cmd=argv[1];

        if(cmd=="info"){
            std::cout << "\nGreen TAC environment\n";
            RaplReader r;
            std::cout << "  Energy provider: " << r.source() << "\n";
            std::cout << "  Real energy     : " << (r.available()?"available":"not available") << "\n";
            std::cout << "  Research rule   : do not treat proxy energy as measured energy.\n\n";
            return 0;
        }
        if(cmd=="energy-check"){
            RaplReader r;
            std::cout<<r.source()<<"\n";
            if(auto e=r.readPackageEnergyJ())std::cout<<"Current package energy: "<<std::setprecision(12)<<*e<<" J\n";
            return r.available()?0:1;
        }
        if(cmd=="demo"){
            std::string path=argc>=3?argv[2]:"benchmarks/cse.c";
            TACProgram p=parseProgram(path);
            std::cout << "\n==================== GREEN TAC DEMO ====================\n";
            std::cout << "Input: " << path << "\n\nProgram features\n"; printFeatureSummary(extractFeatures(p));
            printStrategyTable(p);
            for(Strategy s:{Strategy::Baseline,Strategy::Lightweight,Strategy::DAG}){
                std::cout << "\n### " << strategyName(s) << "\n";
                printTACWithHeader(optimize(p,s));
            }
            std::cout << "\n### Green selector\n";
            return commandSelect(p,"data/model.csv",700.0,200.0,10000.0,0.10);
        }
        if(argc<3){usage();return 2;}

        TACProgram base=parseProgram(argv[2]);
        if(cmd=="tac"){
            Strategy s=argc>=4?parseStrategy(argv[3]):Strategy::Baseline;
            printTACWithHeader(optimize(base,s));
            return 0;
        }
        if(cmd=="compare"){
            std::cout << "\n================ TAC STRATEGY COMPARISON ================\n";
            std::cout << "Input: "<<argv[2]<<"\n";
            printStrategyTable(base);
            for(Strategy s:{Strategy::Baseline,Strategy::Lightweight,Strategy::DAG}){
                std::cout << "\n### "<<strategyName(s)<<"\n";
                printTACWithHeader(optimize(base,s));
            }
            return 0;
        }
        if(cmd=="features"){
            printFeatureSummary(extractFeatures(base));
            return 0;
        }
        if(cmd=="c"){
            if(argc<5){usage();return 2;}
            Strategy s=parseStrategy(argv[3]);
            std::ofstream out(argv[4]); if(!out)throw std::runtime_error("Cannot write output: "+std::string(argv[4]));
            out<<tacToC(optimize(base,s), "program", 1);
            std::cout << "Generated C: " << argv[4] << "\n";
            return 0;
        }
        if(cmd=="select"){
            std::string modelPath=argc>=4?argv[3]:"data/model.csv";
            double compileCI=argc>=5?std::stod(argv[4]):400.0;
            double runtimeCI=argc>=6?std::stod(argv[5]):400.0;
            double executions=argc>=7?std::stod(argv[6]):1000.0;
            double maxOverhead=argc>=8?std::stod(argv[7]):0.10;
            return commandSelect(base,modelPath,compileCI,runtimeCI,executions,maxOverhead);
        }
        usage();return 2;
    }catch(const std::exception& e){std::cerr<<"\nERROR: "<<e.what()<<"\n";return 1;}
}
