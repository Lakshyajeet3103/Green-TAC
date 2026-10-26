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

static void checkHardInputs(){
    const std::vector<std::pair<std::string,std::map<std::string,long long>>> cases={
        {R"(a = 2 + 3 * 4 - 10 / 3 % 2;
b = -(a - 20) * -2;
c = (a + b) * (a - b) / 7 % 5;
p = 2 - 3 - 4; q = 100 / 5 / 2; m = 2 * 3 % 4;)",
         {{"a",13},{"b",-14},{"c",-3},{"p",-5},{"q",10},{"m",2}}},
        {R"(a = 0; b = 0;
t = (a = 1) || (b = 1);
u = (a = 0) && (b = 2);
v = (a = 0) || (b = 3);)", {{"a",0},{"b",3},{"t",1},{"u",0},{"v",1}}},
        {R"(r = ((1 + 2) * (3 - 4 * (5 - 6 / (7 - 5)))) % 7 == -2 || 0 && 1 / 0;
s = 1 || 1 / 0;
k = 0 && (1 % 0);)", {{"r",0},{"s",1},{"k",0}}},
        {R"(a = 5; b = 10; c = 0;
r1 = a < b && b < 20;
r2 = a > b || c;
r3 = !(a == 5) || b != 10 || c >= 0;
r4 = !a && b;
r5 = a < b == 1;
r6 = a <= 5 && b >= 10 && !(c);
r7 = true && false || true;
r8 = !!7;)", {{"r1",1},{"r2",0},{"r3",1},{"r4",0},{"r5",1},{"r6",1},{"r7",1},{"r8",1}}},
        {R"(a = 1; b = 0;
if (a) if (b) r = 1; else r = 2;
x = 7;
if (x > 5 && x < 10 || x == 0) y = 1; else y = 2;)", {{"r",2},{"y",1}}},
        {R"(count = 0; n = 2;
while (n < 30) {
    isp = 1; d = 2;
    while (d * d <= n && isp) {
        if (n % d == 0) isp = 0;
        d = d + 1;
    }
    if (isp) count = count + 1;
    n = n + 1;
})", {{"count",10},{"n",30},{"isp",1},{"d",6}}},
        {R"(a = 3; b = 4; c = 5;
r = !(a < b && b < c) || (a = a + 10) > 12 && !(b == 5) == true;
g = ((a * b - c) % 6 + -(c / 2)) * (a >= b) + (c != 5 || a == 13);)",
         {{"a",13},{"b",4},{"c",5},{"r",1},{"g",4}}},
        {"a=0; b=0; t=(a=1)||(b=1); afterOr=b; u=(a=0)&&(b=2); afterAnd=b;",{{"afterOr",0},{"afterAnd",0}}},
        {"a=1; r=a+(a=2); s=(a=3)+(a=4); q=a<(a=5);",{{"r",3},{"s",7},{"q",1},{"a",5}}},
        {"a=b=c=7; x=+a; while (a) a=a-1; if (-b) x=9;",{{"a",0},{"b",7},{"c",7},{"x",9}}},
        {"t1=10; x=2+3; result=t1+x; t2=20; y=1+2; z=t2+y;",{{"result",15},{"z",23}}},
        {"a=0; if (a) if (1) r=1; else r=2; else r=3;",{{"r",3}}}
    };
    for(const auto& test:cases){
        for(auto strategy:{Strategy::Baseline,Strategy::Lightweight,Strategy::DAG}){
            auto values=execute(optimize(compile(test.first),strategy));
            for(const auto& expected:test.second){
                if(values.at(expected.first)!=expected.second)
                    throw std::runtime_error("Hard input failed: " + strategyName(strategy) + " variable " + expected.first);
            }
        }
        std::ostringstream trace;
        printCompilationSteps(test.first,trace);
        assert(trace.str().find("?")==std::string::npos);
    }
    for(const auto* invalid:{"x=(1=2);", "x=((a+b)=2);", "x=-;", "if (1) x=2; else", "a=(b=);"}){
        bool rejected=false;
        try{compile(invalid);}catch(const std::runtime_error&){rejected=true;}
        assert(rejected);
    }
}

static void checkNamedInputs(){
    struct Case { std::string name, source; std::map<std::string,long long> expected; };
    const std::vector<Case> cases={
        {"A1", R"(a = 2 + 3 * 4 - 10 / 3 % 2; b = -(a - 20) * -2; c = (a + b) * (a - b) / 7 % 5;)", {{"a",13},{"b",-14},{"c",-3}}},
        {"A2", R"(p = 2 - 3 - 4; q = 100 / 5 / 2; m = 2 * 3 % 4;)", {{"p",-5},{"q",10},{"m",2}}},
        {"A3", R"(x = ((((((1 + 2) * 3) - 4) * 5) + 6) * 7) - 8; y = 1 + (2 * (3 + (4 * (5 + (6 * (7 + 8))))));)", {{"x",209},{"y",767}}},
        {"A4", R"(a = - - 3; b = !-0; c = - !0; d = 5 - -3; e = 2 * -3 * -4; f = !0 + !0 * 5;)", {{"a",3},{"b",1},{"c",-1},{"d",8},{"e",24},{"f",6}}},
        {"A5", R"(a = 12; b = 5; a = a + b; b = a - b; a = a - b;)", {{"a",5},{"b",12}}},
        {"B1", R"(x = y = z = 5; w = (x = x + 1) * (y = y + 2) + z;)", {{"x",6},{"y",7},{"z",5},{"w",47}}},
        {"C1", R"(a = 5; b = 10; c = 0; r1 = a < b && b < 20; r2 = a > b || c; r3 = !(a == 5) || b != 10 || c >= 0; r4 = !a && b; r5 = a < b == 1; r6 = a <= 5 && b >= 10 && !(c); r7 = true && false || true; r8 = !!7;)", {{"r1",1},{"r2",0},{"r3",1},{"r4",0},{"r5",1},{"r6",1},{"r7",1},{"r8",1}}},
        {"C2", R"(a = 1 < 2 < 3; b = 3 > 2 > 1; c = 5 == 5 == 1; d = 2 < 1 == 0; e = 1 != 2 != 2; f = 10 > 5 == 3 > 1;)", {{"a",1},{"b",0},{"c",1},{"d",1},{"e",1},{"f",1}}},
        {"C3", R"(a = 7; b = 3; s = (a > b) + (a < b) + (a == 7) * 10 + (a != b && b) * 100 + (a < b || b > 5) * 1000;)", {{"s",111}}},
        {"D1", R"(a = 0; b = 0; t = (a = 1) || (b = 1); u = (a = 0) && (b = 2); v = (a = 0) || (b = 3);)", {{"a",0},{"b",3},{"t",1},{"u",0},{"v",1}}},
        {"D2", R"(r = ((1 + 2) * (3 - 4 * (5 - 6 / (7 - 5)))) % 7 == -2 || 0 && 1 / 0; s = 1 || 1 / 0; k = 0 && (1 % 0);)", {{"r",0},{"s",1},{"k",0}}},
        {"D3", R"(c = 0; r = (c = c + 1) > 5 && (c = c + 10) > 0 || (c = c + 100) > 50 && (c = c + 1000) > 0; d = 0; s = ((d = d + 1) || (d = d + 10)) && ((d = d + 100) > 100 || (d = d + 1000)); e = 0; u = !((e = 1) && (e = 2) && (e = 0)) || (e = 99);)", {{"r",1},{"c",1101},{"s",1},{"d",101},{"u",1},{"e",0}}},
        {"D4", R"(r = (a = 1) && (b = 2) && (c = 3) && (d = 0) && (e = 5) && (f = 6); q = (a = 0) || (b = 0) || (c = 7) || (d = 8) || (e = 9);)", {{"r",0},{"q",1},{"a",0},{"b",0},{"c",7},{"d",0}}},
        {"E1", R"(a = 3; b = 4; c = 5; r = !(a < b && b < c) || (a = a + 10) > 12 && !(b == 5) == true; g = ((a * b - c) % 6 + -(c / 2)) * (a >= b) + (c != 5 || a == 13);)", {{"a",13},{"b",4},{"c",5},{"r",1},{"g",4}}},
        {"F1", R"(a = 1; b = 0; if (a) if (b) r = 1; else r = 2;)", {{"r",2}}},
        {"F2", R"(n = 10; a = 0; b = 1; i = 0; while (i < n) { t = a + b; a = b; b = t; i = i + 1; })", {{"a",55},{"b",89}}},
        {"F3", R"(count = 0; n = 2; while (n < 30) { isp = 1; d = 2; while (d * d <= n && isp) { if (n % d == 0) isp = 0; d = d + 1; } if (isp) count = count + 1; n = n + 1; })", {{"count",10}}},
    };
    for(const auto& test:cases){
        for(auto strategy:{Strategy::Baseline,Strategy::Lightweight,Strategy::DAG}){
            auto values=execute(optimize(compile(test.source),strategy));
            for(const auto& expected:test.expected){
                if(values.at(expected.first)!=expected.second)
                    throw std::runtime_error(test.name + " failed in " + strategyName(strategy) + ": " + expected.first);
            }
            if(test.name=="D4" && (values.count("e") || values.count("f")))
                throw std::runtime_error("D4 executed a skipped assignment in " + strategyName(strategy));
        }
    }
    std::cout << "A1-F3: all 17 inputs passed in all 3 strategies (51 executions).\n";
}

int main(){
    checkNamedInputs();
    checkHardInputs();
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
