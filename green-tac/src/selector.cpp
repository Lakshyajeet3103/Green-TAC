#include "greentac/selector.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace greentac {
static double predict(const std::map<Strategy,std::map<std::string,double>>& models, Strategy s, const std::map<std::string,double>& feats){
    auto it=models.find(s); if(it==models.end())return -1.0;
    double y=0; auto c=it->second.find("intercept");if(c!=it->second.end())y+=c->second;
    for(const auto& [k,v]:feats){auto q=it->second.find(k);if(q!=it->second.end())y+=q->second*v;}
    return std::max(0.0,y);
}

Model loadModel(const std::string& path){
    Model m;
    std::ifstream in(path);
    if(!in)return m;
    std::string line;
    while(std::getline(in,line)){
        if(line.empty()||line[0]=='#')continue;
        std::stringstream ss(line);std::string strategy,metric,feature,val;
        std::getline(ss,strategy,',');std::getline(ss,metric,',');std::getline(ss,feature,',');std::getline(ss,val,',');
        if(strategy!="baseline"&&strategy!="lightweight"&&strategy!="dag")continue;
        Strategy s=strategy=="baseline"?Strategy::Baseline:strategy=="lightweight"?Strategy::Lightweight:Strategy::DAG;
        double d=std::stod(val);
        if(metric=="compile_energy") m.compileEnergy[s][feature]=d;
        else if(metric=="runtime_energy") m.runtimeEnergy[s][feature]=d;
        else if(metric=="runtime_ms") m.runtimeMs[s][feature]=d;
    }
    auto complete=[](const auto& x){
        return x.size()==3 && std::all_of(x.begin(),x.end(),[](const auto& kv){return kv.second.find("intercept")!=kv.second.end();});
    };
    m.hasCompileEnergy=complete(m.compileEnergy);
    m.hasRuntimeEnergy=complete(m.runtimeEnergy);
    m.hasRuntimeMs=complete(m.runtimeMs);
    m.fullyCalibrated=m.hasCompileEnergy&&m.hasRuntimeEnergy&&m.hasRuntimeMs;
    return m;
}

static double fallbackCompileEnergy(const Features& f, Strategy s) {
    // Transparent proxy only. These are not physical energy measurements.
    const double base = 0.20*f.instructions + 0.55*f.binary_ops + 0.30*f.basic_blocks;
    switch(s) {
        case Strategy::Baseline: return base;
        case Strategy::Lightweight: return base + 0.35*f.binary_ops + 0.75;
        case Strategy::DAG: return base + 0.55*f.binary_ops + 1.25*f.common_subexpressions + 1.50;
    }
    return base;
}

static double fallbackRuntimeEnergy(const Features& f) {
    return 0.90*f.instructions + 1.60*f.binary_ops + 2.20*f.branches + 0.40*f.temporaries;
}

static double fallbackRuntimeMs(const Features& f) {
    return 0.010*f.instructions + 0.020*f.binary_ops + 0.050*f.branches;
}

SelectionResult selectStrategy(const TACProgram& baseline,const Features& features,const Model& model,const SelectionConfig& cfg){
    auto fm=featureMap(features);
    SelectionResult r; r.selected=Strategy::Baseline; double best=1e300;
    const Features baselineFeatures = extractFeatures(baseline);

    double baseRT = model.hasRuntimeMs ? predict(model.runtimeMs,Strategy::Baseline,fm) : fallbackRuntimeMs(baselineFeatures);
    if(baseRT < 0.0) baseRT = fallbackRuntimeMs(baselineFeatures);

    for(Strategy s:{Strategy::Baseline,Strategy::Lightweight,Strategy::DAG}){
        TACProgram opt=optimize(baseline,s);
        Features fo=extractFeatures(opt);

        double cE = model.hasCompileEnergy ? predict(model.compileEnergy,s,fm) : fallbackCompileEnergy(features,s);
        if(cE < 0.0) cE = fallbackCompileEnergy(features,s);

        double rE = model.hasRuntimeEnergy ? predict(model.runtimeEnergy,s,fm) : fallbackRuntimeEnergy(fo);
        if(rE < 0.0) rE = fallbackRuntimeEnergy(fo);

        double rt = model.hasRuntimeMs ? predict(model.runtimeMs,s,fm) : fallbackRuntimeMs(fo);
        if(rt < 0.0) rt = fallbackRuntimeMs(fo);

        bool allowed=baseRT<=0 || rt<=baseRT*(1.0+cfg.maxRuntimeOverBaseline);
        auto ce=estimateCarbon(cE,rE,rt,cfg.carbon);
        CandidatePrediction cp{s,cE,rE,rt,ce.totalCarbonGrams,allowed};
        r.candidates.push_back(cp);
        if(allowed&&ce.totalCarbonGrams<best){best=ce.totalCarbonGrams;r.selected=s;}
    }
    return r;
}
}
