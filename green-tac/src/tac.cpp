#include "greentac/tac.h"
#include <sstream>
namespace greentac {
std::string TACProgram::newTemp(){return "t"+std::to_string(++tempCount);} 
std::string TACProgram::newLabel(const std::string& prefix){ static int n=0; return prefix+std::to_string(++n); }
void TACProgram::print(std::ostream& os) const { for(const auto& i:code){ switch(i.kind){case TACKind::Assign:os<<i.result<<" = "<<i.arg1;break;case TACKind::Binary:os<<i.result<<" = "<<i.arg1<<" "<<i.op<<" "<<i.arg2;break;case TACKind::Label:os<<i.label<<":";break;case TACKind::Goto:os<<"goto "<<i.label;break;case TACKind::IfGoto:os<<"if "<<i.arg1<<" "<<i.op<<" "<<i.arg2<<" goto "<<i.label;break;} os<<'\n'; } }
TACProgram TACGenerator::generate(const Program& p){out_=TACProgram{};for(const auto& s:p.statements)genStmt(s.get());return std::move(out_);} 
std::string TACGenerator::genExpr(const Expr* e){
    if(auto n=dynamic_cast<const NumberExpr*>(e)) return std::to_string(n->value);
    if(auto v=dynamic_cast<const VarExpr*>(e)){out_.variables.insert(v->name);return v->name;}
    auto b=dynamic_cast<const BinaryExpr*>(e); if(!b) throw std::runtime_error("Unknown expression");
    std::string l=genExpr(b->lhs.get()), r=genExpr(b->rhs.get()), t=out_.newTemp(); out_.variables.insert(t); out_.code.push_back({TACKind::Binary,t,l,r,b->op,{}}); return t;
}
void TACGenerator::genStmt(const Stmt* s){
    if(auto a=dynamic_cast<const AssignStmt*>(s)){std::string v=genExpr(a->expr.get());out_.variables.insert(a->name);out_.code.push_back({TACKind::Assign,a->name,v,"","",{}});return;}
    if(auto b=dynamic_cast<const BlockStmt*>(s)){genBlock(b);return;}
    if(auto i=dynamic_cast<const IfStmt*>(s)){
        if(auto c=dynamic_cast<const BinaryExpr*>(i->cond.get())){
            std::string l=genExpr(c->lhs.get()), r=genExpr(c->rhs.get()), thenL=out_.newLabel("L_then"), endL=out_.newLabel("L_end");
            std::string elseL=i->elseBlock?out_.newLabel("L_else"):endL; out_.code.push_back({TACKind::IfGoto,"",l,r,c->op,thenL}); out_.code.push_back({TACKind::Goto,"","","","",elseL});
            out_.code.push_back({TACKind::Label,"","","","",thenL}); genBlock(i->thenBlock.get()); out_.code.push_back({TACKind::Goto,"","","","",endL});
            if(i->elseBlock){out_.code.push_back({TACKind::Label,"","","","",elseL});genBlock(i->elseBlock.get());}
            out_.code.push_back({TACKind::Label,"","","","",endL}); return;
        }
        throw std::runtime_error("if condition must be a comparison");
    }
    if(auto w=dynamic_cast<const WhileStmt*>(s)){
        if(auto c=dynamic_cast<const BinaryExpr*>(w->cond.get())){
            std::string head=out_.newLabel("L_while"), body=out_.newLabel("L_body"), end=out_.newLabel("L_end"); out_.code.push_back({TACKind::Label,"","","","",head});
            std::string l=genExpr(c->lhs.get()), r=genExpr(c->rhs.get()); out_.code.push_back({TACKind::IfGoto,"",l,r,c->op,body}); out_.code.push_back({TACKind::Goto,"","","","",end}); out_.code.push_back({TACKind::Label,"","","","",body}); genBlock(w->body.get()); out_.code.push_back({TACKind::Goto,"","","","",head}); out_.code.push_back({TACKind::Label,"","","","",end}); return;
        }
        throw std::runtime_error("while condition must be a comparison");
    }
    throw std::runtime_error("Unknown statement");
}
void TACGenerator::genBlock(const BlockStmt* b){for(const auto& s:b->statements)genStmt(s.get());}
}
