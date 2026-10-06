#include "greentac/optimizer.h"
#include <unordered_map>
#include <unordered_set>
#include <stdexcept>
#include <algorithm>

namespace greentac {
std::string strategyName(Strategy s){
    switch(s){case Strategy::Baseline:return "baseline";case Strategy::Lightweight:return "lightweight";case Strategy::DAG:return "dag";}
    return "unknown";
}

static bool isInt(const std::string& s,long long& v){
    if(s.empty()) return false;
    size_t p=0;
    try{v=std::stoll(s,&p);return p==s.size();}catch(...){return false;}
}
static std::string fold(const std::string& op,const std::string& a,const std::string& b){
    long long x,y; if(!isInt(a,x)||!isInt(b,y)) return {};
    long long z=0;
    if(op=="+")z=x+y; else if(op=="-")z=x-y; else if(op=="*")z=x*y; else if(op=="/"&&y!=0)z=x/y; else if(op=="%"&&y!=0)z=x%y; else return {};
    return std::to_string(z);
}
static std::string algebraic(const std::string& op,const std::string& a,const std::string& b){
    if(op=="+"&&b=="0")return a;
    if(op=="+"&&a=="0")return b;
    if(op=="-"&&b=="0")return a;
    if(op=="*"&&b=="1")return a;
    if(op=="*"&&a=="1")return b;
    if(op=="*"&&(a=="0"||b=="0"))return "0";
    return {};
}

static bool chainDependsOn(const std::unordered_map<std::string,std::string>& copies, const std::string& value, const std::string& target){
    std::string x=value; std::unordered_set<std::string> seen;
    while(copies.count(x) && !seen.count(x)){
        if(x==target) return true;
        seen.insert(x); x=copies.at(x);
    }
    return x==target;
}

static void invalidate(const std::string& target, std::unordered_map<std::string,std::string>& copies){
    for(auto it=copies.begin();it!=copies.end();){
        if(it->first==target || chainDependsOn(copies,it->second,target)) it=copies.erase(it); else ++it;
    }
}

static TACProgram lightweightImpl(const TACProgram& in){
    TACProgram out; out.tempCount=in.tempCount;
    std::unordered_map<std::string,std::string> copies;
    auto resolve=[&](std::string x){
        std::unordered_set<std::string> seen;
        while(copies.count(x)&&!seen.count(x)){seen.insert(x);x=copies[x];}
        return x;
    };
    for(auto ins:in.code){
        if(ins.kind==TACKind::Binary){
            ins.arg1=resolve(ins.arg1); ins.arg2=resolve(ins.arg2);
            if(auto f=fold(ins.op,ins.arg1,ins.arg2);!f.empty()){
                invalidate(ins.result,copies);
                ins.kind=TACKind::Assign; ins.arg1=f; ins.arg2.clear(); ins.op.clear();
                copies[ins.result]=f;
            }else if(auto a=algebraic(ins.op,ins.arg1,ins.arg2);!a.empty()){
                invalidate(ins.result,copies);
                ins.kind=TACKind::Assign; ins.arg1=a; ins.arg2.clear(); ins.op.clear();
                copies[ins.result]=a;
            }else{
                invalidate(ins.result,copies);
            }
        }else if(ins.kind==TACKind::Assign){
            ins.arg1=resolve(ins.arg1);
            invalidate(ins.result,copies);
            copies[ins.result]=ins.arg1;
        }else if(ins.kind==TACKind::IfGoto){
            ins.arg1=resolve(ins.arg1); ins.arg2=resolve(ins.arg2);
        }else if(ins.kind==TACKind::Goto || ins.kind==TACKind::Label){
            // Control-flow boundaries make this simple forward analysis conservative.
            copies.clear();
        }
        out.code.push_back(std::move(ins));
    }
    return out;
}

static TACProgram dagImpl(const TACProgram& in){
    TACProgram out; out.tempCount=in.tempCount;
    std::unordered_map<std::string,std::string> exprToTemp; std::unordered_map<std::string,std::string> alias;
    auto resolve=[&](std::string x){std::unordered_set<std::string> seen;while(alias.count(x)&&!seen.count(x)){seen.insert(x);x=alias[x];}return x;};
    auto flush=[&](){exprToTemp.clear();alias.clear();};
    for(auto ins:in.code){
        if(ins.kind==TACKind::Binary){
            ins.arg1=resolve(ins.arg1); ins.arg2=resolve(ins.arg2);
            std::string key=ins.op+"|"+ins.arg1+"|"+ins.arg2;
            if(exprToTemp.count(key)){alias[ins.result]=exprToTemp[key];continue;}
            exprToTemp[key]=ins.result; alias.erase(ins.result); out.code.push_back(std::move(ins));
        }else if(ins.kind==TACKind::Assign){
            ins.arg1=resolve(ins.arg1); flush(); alias[ins.result]=ins.arg1; out.code.push_back(std::move(ins));
        }else if(ins.kind==TACKind::IfGoto){
            ins.arg1=resolve(ins.arg1); ins.arg2=resolve(ins.arg2); out.code.push_back(std::move(ins)); flush();
        }else{
            out.code.push_back(std::move(ins)); flush();
        }
    }
    return out;
}

TACProgram optimize(const TACProgram& input, Strategy s){
    switch(s){case Strategy::Baseline:return input;case Strategy::Lightweight:return lightweightImpl(input);case Strategy::DAG:return dagImpl(lightweightImpl(input));}
    return input;
}
}
