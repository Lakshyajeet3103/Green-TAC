#include "greentac/codegen_c.h"
#include <sstream>
#include <set>
#include <algorithm>

namespace greentac {
static bool isNumber(const std::string& x){
    if(x.empty()) return false;
    size_t p=0; try{std::stoll(x,&p);return p==x.size();}catch(...){return false;}
}
std::string tacToC(const TACProgram& p,const std::string& functionName,int executions){
    executions=std::max(1,executions);
    std::ostringstream out; std::set<std::string> vars;
    for(const auto& v:p.variables)if(!isNumber(v))vars.insert(v);
    for(const auto& i:p.code){
        if(!i.result.empty()&&!isNumber(i.result))vars.insert(i.result);
        if(!i.arg1.empty()&&!isNumber(i.arg1))vars.insert(i.arg1);
        if(!i.arg2.empty()&&!isNumber(i.arg2))vars.insert(i.arg2);
    }
    out<<"#include <stdio.h>\n\nint "<<functionName<<"(void) {\n";
    for(const auto& v:vars) out<<"    int "<<v<<" = 0;\n";
    for(const auto& i:p.code){
        out<<"    ";
        switch(i.kind){
            case TACKind::Assign: out<<i.result<<" = "<<i.arg1<<";"; break;
            case TACKind::Binary: out<<i.result<<" = "<<i.arg1<<" "<<i.op<<" "<<i.arg2<<";"; break;
            case TACKind::Label: out<<i.label<<":"; break;
            case TACKind::Goto: out<<"goto "<<i.label<<";"; break;
            case TACKind::IfGoto: out<<"if ("<<i.arg1<<" "<<i.op<<" "<<i.arg2<<") goto "<<i.label<<";"; break;
        }
        out<<"\n";
    }
    out<<"    return 0;\n}\n\nint main(void){\n";
    out<<"    int rc = 0;\n    for (int i = 0; i < "<<executions<<"; ++i) rc |= "<<functionName<<"();\n    return rc;\n}\n";
    return out.str();
}
}
