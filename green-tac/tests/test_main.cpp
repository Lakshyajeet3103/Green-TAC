#include "greentac/steps.h"
#include "greentac/lexer.h"
#include "greentac/parser.h"
#include "greentac/tac.h"
#include "greentac/optimizer.h"
#include "greentac/features.h"
#include "greentac/selector.h"
#include <cassert>
#include <sstream>
#include <iostream>
#include <map>
#include <stdexcept>
using namespace greentac;
static TACProgram compile(const std::string& s){return TACGenerator().generate(Parser(Lexer(s).lex()).parse());}
static std::string text(const TACProgram& p){std::ostringstream ss;p.print(ss);return ss.str();}
// Execute the emitted TAC so tests verify semantics across every optimizer.
static std::map<std::string,long long> execute(const TACProgram& p){
    std::map<std::string,long long> values;
    std::map<std::string,std::size_t> labels;
    for(std::size_t i=0;i<p.code.size();++i)
        if(p.code[i].kind==TACKind::Label) labels[p.code[i].label]=i;
    auto value=[&](const std::string& x)->long long {
        if(!x.empty() && (x[0]=='-' || (x[0]>='0' && x[0]<='9'))) return std::stoll(x);
        return values[x];
    };
    auto eval=[](const std::string& op,long long a,long long b)->long long {
        if(op=="+") return a+b;
        if(op=="-") return a-b;
        if(op=="*") return a*b;
        if(op=="/" || op=="%") {
            if(b==0) throw std::runtime_error("Short-circuit failure: division by zero");
            return op=="/"?a/b:a%b;
        }
        if(op=="<") return a<b;
        if(op=="<=") return a<=b;
        if(op==">") return a>b;
        if(op==">=") return a>=b;
        if(op=="==") return a==b;
        if(op=="!=") return a!=b;
        throw std::runtime_error("Unknown TAC operator");
    };
    std::size_t pc=0,steps=0;
    while(pc<p.code.size()){
        if(++steps>10000) throw std::runtime_error("Loop did not terminate");
        const auto& i=p.code[pc++];
        switch(i.kind){
        case TACKind::Assign: values[i.result]=value(i.arg1);break;
        case TACKind::Binary: values[i.result]=eval(i.op,value(i.arg1),value(i.arg2));break;
        case TACKind::Label: break;
        case TACKind::Goto: pc=labels.at(i.label);break;
        case TACKind::IfGoto: if(eval(i.op,value(i.arg1),value(i.arg2))) pc=labels.at(i.label);break;
        }
    }
    return values;
}
static void checkBooleanPrograms(){
    const std::vector<std::pair<std::string,long long>> cases={
        {"result = true || false && false;",1},
        {"result = (true || false) && false;",0},
        {"result = !2 + 3;",3},
        {"result = !!7;",1},
        {"result = 2 == 3 < 4;",0},
        {"result = !(2 < 3) || 4 >= 4 && 5 != 6;",1},
        {"result = 7 && 9;",1},
        {"result = 0 || 9;",1},
        {"result = 0 && (1 / 0);",0},
        {"result = 1 || (1 / 0);",1},
        {"result = !(0 && (1 / 0));",1},
        {"result = (2 && 3) + (0 || 8);",2},
        {"result = 0; if (false && 1 / 0) { result = 9; } else if (!false) { result = 4; } else { result = 8; }",4},
        {"result = 0; if (true || 1 / 0) { if (3) { result = 6; } }",6},
        {"result = 0; if (1 - 1) { result = 9; }",0},
        {"result = 0; while (result < 4 && !(result == 3)) { result = result + 1; }",3},
        {"result = 3; while (result) { result = result - 1; }",0},
        {"result = 0; while (false && 1 / 0) { result = 1; }",0},
        {"result = 0; i = 0; while (i < 2) { j = 0; while (j < 3 && i != 2) { result = result + 1; j = j + 1; } i = i + 1; }",6}
    };
    for(const auto& test:cases)
        for(auto strategy:{Strategy::Baseline,Strategy::Lightweight,Strategy::DAG})
            assert(execute(optimize(compile(test.first),strategy)).at("result")==test.second);
    for(const auto* invalid:{"x = a & b;", "x = a | b;", "x = !;", "x = a &&;"}){
        bool rejected=false;
        try{compile(invalid);}catch(const std::runtime_error&){rejected=true;}
        assert(rejected);
    }
    std::ostringstream trace;
    printCompilationSteps("flag = !(a < b) || true;",trace);
    assert(trace.str().find("?")==std::string::npos);
    assert(trace.str().find("L_rhs")!=std::string::npos);
}
int main(){
    checkBooleanPrograms();
    auto p=compile("x = a + b * c;"); assert(p.code.size()==3);
    auto d=compile("x = (a+b) * (a+b) + (a+b);"); auto od=optimize(d,Strategy::DAG); assert(od.code.size()<d.code.size());
    auto l=compile("x = 2 + 3; y = x * 1;"); auto ol=optimize(l,Strategy::Lightweight); auto str=text(ol); assert(str.find("x = 5")!=std::string::npos); assert(str.find("y = 5")!=std::string::npos);
    auto h=compile("x = a + b; a = 10; y = a + b;"); auto oh=optimize(h,Strategy::DAG); auto hstr=text(oh); assert(hstr.find("y = t1")==std::string::npos);
    auto loop=compile("x = 0; while (x < 10) { x = x + 1; }"); auto f=extractFeatures(loop); assert(f.labels==3); assert(f.branches==1); assert(f.basic_blocks>=3); assert(f.max_expr_depth>=1);
    auto example=compile("a = 10 + 20; b = a * 1; c = b + 0; d = (x+y)*(x+y); e = (x+y)+(x+y); f = 5*6; g = d+f; h = (x+y)*1;");
    auto ef=extractFeatures(example);
    SelectionConfig cfg;
    cfg.carbon.compileCI_g_per_kWh=700;
    cfg.carbon.runtimeCI_g_per_kWh=200;
    cfg.carbon.expectedExecutions=1;
    assert(selectStrategy(example,ef,Model{},cfg).selected==Strategy::Baseline);
    cfg.carbon.expectedExecutions=3;
    assert(selectStrategy(example,ef,Model{},cfg).selected==Strategy::Lightweight);
    cfg.carbon.expectedExecutions=10;
    assert(selectStrategy(example,ef,Model{},cfg).selected==Strategy::DAG);
    cfg.carbon.expectedExecutions=1;
    cfg.carbon.compileCI_g_per_kWh=200;
    cfg.carbon.runtimeCI_g_per_kWh=700;
    assert(selectStrategy(example,ef,Model{},cfg).selected==Strategy::DAG);
    Model constrained;
    constrained.hasRuntimeMs=true;
    constrained.runtimeMs[Strategy::Baseline]["intercept"]=1;
    constrained.runtimeMs[Strategy::Lightweight]["intercept"]=2;
    constrained.runtimeMs[Strategy::DAG]["intercept"]=2;
    auto blocked=selectStrategy(example,ef,constrained,cfg);
    assert(blocked.selected==Strategy::Baseline);
    assert(blocked.candidates[0].allowed && !blocked.candidates[1].allowed && !blocked.candidates[2].allowed);
    std::ostringstream trace;
    assert(text(optimizeWithSteps(d,trace))==text(od));
    assert(trace.str().find("Reuse n")!=std::string::npos);
    assert(trace.str().find("lhs: n")!=std::string::npos);
    std::ostringstream tree;
    printCompilationSteps("while (a < 3) { if (a == 1) { x = a + 1; } else { x = 0; } a = a + 1; }",tree);
    for(const auto* label:{"1. Tokens", "2. Abstract syntax tree", "While", "then:", "else:", "3. Baseline TAC", "6. Final"})
        assert(tree.str().find(label)!=std::string::npos);
    std::ostringstream empty;
    printCompilationSteps("",empty);
    assert(empty.str().find("<end>")!=std::string::npos);
    std::cout<<"All tests passed.\n";
}
