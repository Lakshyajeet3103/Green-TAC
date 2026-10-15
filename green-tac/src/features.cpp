#include "greentac/features.h"
#include <algorithm>
#include <unordered_map>
#include <unordered_set>

namespace greentac {
Features extractFeatures(const TACProgram& p){
    Features f;
    f.instructions = static_cast<double>(p.code.size());
    std::unordered_set<std::string> temps;
    std::unordered_set<std::string> exprs;
    std::unordered_map<std::string, int> depth;
    bool newBlock = !p.code.empty();

    auto operandDepth = [&](const std::string& x) {
        auto it = depth.find(x);
        return it == depth.end() ? 0 : it->second;
    };

    for(std::size_t idx=0; idx<p.code.size(); ++idx){
        const auto& i = p.code[idx];
        if(newBlock){ f.basic_blocks += 1.0; newBlock=false; }

        if(i.kind==TACKind::Binary){
            ++f.binary_ops;
            if(i.result.rfind("t",0)==0) temps.insert(i.result);
            if(i.op=="<"||i.op=="<="||i.op==">"||i.op==">="||i.op=="=="||i.op=="!=") ++f.comparisons;
            std::string key=i.op+"|"+i.arg1+"|"+i.arg2;
            if(!exprs.insert(key).second) ++f.common_subexpressions;
            int d = 1 + std::max(operandDepth(i.arg1), operandDepth(i.arg2));
            depth[i.result] = d;
            f.max_expr_depth = std::max(f.max_expr_depth, static_cast<double>(d));
        } else if(i.kind==TACKind::Assign){
            if(i.result.rfind("t",0)==0) temps.insert(i.result);
            depth[i.result] = operandDepth(i.arg1);
            if(!i.arg1.empty()) ++f.memory_ops;
        } else if(i.kind==TACKind::IfGoto){
            ++f.branches;
            ++f.comparisons;
            newBlock=true;
        } else if(i.kind==TACKind::Goto){
            newBlock=true;
        } else if(i.kind==TACKind::Label){
            ++f.labels;
            if(idx>0) newBlock=true;
        }
    }
    f.temporaries=static_cast<double>(temps.size());
    return f;
}

std::map<std::string,double> featureMap(const Features& f){
    return {
        {"instructions",f.instructions},
        {"binary_ops",f.binary_ops},
        {"branches",f.branches},
        {"labels",f.labels},
        {"temporaries",f.temporaries},
        {"memory_ops",f.memory_ops},
        {"comparisons",f.comparisons},
        {"basic_blocks",f.basic_blocks},
        {"max_expr_depth",f.max_expr_depth},
        {"common_subexpressions",f.common_subexpressions}
    };
}
}
