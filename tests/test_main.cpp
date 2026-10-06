#include "greentac/lexer.h"
#include "greentac/parser.h"
#include "greentac/tac.h"
#include "greentac/optimizer.h"
#include "greentac/features.h"
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
    std::cout<<"All tests passed.\n";
}
