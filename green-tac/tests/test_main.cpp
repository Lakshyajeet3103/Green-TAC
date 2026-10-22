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
using namespace greentac;
static TACProgram compile(const std::string& s){return TACGenerator().generate(Parser(Lexer(s).lex()).parse());}
static std::string text(const TACProgram& p){std::ostringstream ss;p.print(ss);return ss.str();}
int main(){
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
