#include "greentac/tac.h"
#include <sstream>
#include <functional>
namespace greentac {
std::string TACProgram::newTemp(){std::string name; do { name="t"+std::to_string(++tempCount); } while(variables.count(name)); return name;}
std::string TACProgram::newLabel(const std::string& prefix){ static int n=0; return prefix+std::to_string(++n); }
void TACProgram::print(std::ostream& os) const { for(const auto& i:code){ switch(i.kind){case TACKind::Assign:os<<i.result<<" = "<<i.arg1;break;case TACKind::Binary:os<<i.result<<" = "<<i.arg1<<" "<<i.op<<" "<<i.arg2;break;case TACKind::Label:os<<i.label<<":";break;case TACKind::Goto:os<<"goto "<<i.label;break;case TACKind::IfGoto:os<<"if "<<i.arg1<<" "<<i.op<<" "<<i.arg2<<" goto "<<i.label;break;} os<<'\n'; } }
TACProgram TACGenerator::generate(const Program& p){out_=TACProgram{};
    // Reserve every source identifier before allocating any temporary.
    std::function<void(const Expr*)> expr;
    std::function<void(const Stmt*)> stmt;
    expr=[&](const Expr* e){
        if(auto v=dynamic_cast<const VarExpr*>(e)) out_.variables.insert(v->name);
        if(auto a=dynamic_cast<const AssignExpr*>(e)){out_.variables.insert(a->name);expr(a->value.get());}
        if(auto u=dynamic_cast<const UnaryExpr*>(e)) expr(u->operand.get());
        if(auto b=dynamic_cast<const BinaryExpr*>(e)){expr(b->lhs.get());expr(b->rhs.get());}
    };
    stmt=[&](const Stmt* s){
        if(auto a=dynamic_cast<const AssignStmt*>(s)){out_.variables.insert(a->name);expr(a->expr.get());}
        if(auto b=dynamic_cast<const BlockStmt*>(s)) for(const auto& child:b->statements) stmt(child.get());
        if(auto i=dynamic_cast<const IfStmt*>(s)){expr(i->cond.get());stmt(i->thenBlock.get());stmt(i->elseBlock.get());}
        if(auto w=dynamic_cast<const WhileStmt*>(s)){expr(w->cond.get());stmt(w->body.get());}
    };
    for(const auto& s:p.statements) stmt(s.get());
    for(const auto& s:p.statements) genStmt(s.get());
    return std::move(out_);
}
static bool hasAssignment(const Expr* e){
    if(dynamic_cast<const AssignExpr*>(e)) return true;
    if(auto u=dynamic_cast<const UnaryExpr*>(e)) return hasAssignment(u->operand.get());
    if(auto b=dynamic_cast<const BinaryExpr*>(e)) return hasAssignment(b->lhs.get()) || hasAssignment(b->rhs.get());
    return false;
}
std::string TACGenerator::genExpr(const Expr* e){
    if(auto n=dynamic_cast<const NumberExpr*>(e)) return std::to_string(n->value);
    if(auto v=dynamic_cast<const VarExpr*>(e)){out_.variables.insert(v->name);return v->name;}
    if(auto a=dynamic_cast<const AssignExpr*>(e)){
        auto value=genExpr(a->value.get()), t=out_.newTemp(); out_.variables.insert(t);
        out_.code.push_back({TACKind::Assign,t,value,"","",{}});
        out_.code.push_back({TACKind::Assign,a->name,t,"","",{}});
        return t;
    }
    if(auto u=dynamic_cast<const UnaryExpr*>(e); u && u->op!="!"){
        auto value=genExpr(u->operand.get());
        if(u->op=="+") return value;
        auto t=out_.newTemp(); out_.variables.insert(t);
        out_.code.push_back({TACKind::Binary,t,"0",value,"-",{}}); return t;
    }
    auto b=dynamic_cast<const BinaryExpr*>(e);
    if(dynamic_cast<const UnaryExpr*>(e) || (b && (b->op=="&&" || b->op=="||"))){
        // Materialize a Boolean value only after the short-circuit branches.
        auto t=out_.newTemp(); out_.variables.insert(t);
        auto yes=out_.newLabel("L_true"), no=out_.newLabel("L_false"), end=out_.newLabel("L_bool_end");
        genCondition(e,yes,no);
        out_.code.push_back({TACKind::Label,"","","","",yes});
        out_.code.push_back({TACKind::Assign,t,"1","","",{}});
        out_.code.push_back({TACKind::Goto,"","","","",end});
        out_.code.push_back({TACKind::Label,"","","","",no});
        out_.code.push_back({TACKind::Assign,t,"0","","",{}});
        out_.code.push_back({TACKind::Label,"","","","",end});
        return t;
    }
    if(!b) throw std::runtime_error("Unknown expression");
    std::string l=genExpr(b->lhs.get());
    if(hasAssignment(b->rhs.get())){
        auto saved=out_.newTemp(); out_.variables.insert(saved);
        out_.code.push_back({TACKind::Assign,saved,l,"","",{}}); l=saved;
    }
    auto r=genExpr(b->rhs.get()), t=out_.newTemp(); out_.variables.insert(t); out_.code.push_back({TACKind::Binary,t,l,r,b->op,{}}); return t;
}
void TACGenerator::genCondition(const Expr* e,const std::string& yes,const std::string& no){
    if(auto u=dynamic_cast<const UnaryExpr*>(e); u && u->op=="!"){
        genCondition(u->operand.get(),no,yes); return;
    }
    if(auto b=dynamic_cast<const BinaryExpr*>(e)){
        if(b->op=="&&" || b->op=="||"){
            auto rhs=out_.newLabel("L_rhs");
            if(b->op=="&&") genCondition(b->lhs.get(),rhs,no);
            else genCondition(b->lhs.get(),yes,rhs);
            out_.code.push_back({TACKind::Label,"","","","",rhs});
            genCondition(b->rhs.get(),yes,no); return;
        }
        if(b->op=="<"||b->op=="<="||b->op==">"||b->op==">="||b->op=="=="||b->op=="!="){
            auto l=genExpr(b->lhs.get());
            if(hasAssignment(b->rhs.get())){
                auto saved=out_.newTemp(); out_.variables.insert(saved);
                out_.code.push_back({TACKind::Assign,saved,l,"","",{}}); l=saved;
            }
            auto r=genExpr(b->rhs.get());
            out_.code.push_back({TACKind::IfGoto,"",l,r,b->op,yes});
            out_.code.push_back({TACKind::Goto,"","","","",no}); return;
        }
    }
    // Integer truthiness: zero is false; every nonzero value is true.
    auto value=genExpr(e);
    out_.code.push_back({TACKind::IfGoto,"",value,"0","!=",yes});
    out_.code.push_back({TACKind::Goto,"","","","",no});
}
void TACGenerator::genStmt(const Stmt* s){
    if(auto a=dynamic_cast<const AssignStmt*>(s)){std::string v=genExpr(a->expr.get());out_.variables.insert(a->name);out_.code.push_back({TACKind::Assign,a->name,v,"","",{}});return;}
    if(auto b=dynamic_cast<const BlockStmt*>(s)){genBlock(b);return;}
    if(auto i=dynamic_cast<const IfStmt*>(s)){
        auto thenL=out_.newLabel("L_then"), endL=out_.newLabel("L_end");
        auto elseL=i->elseBlock?out_.newLabel("L_else"):endL;
        genCondition(i->cond.get(),thenL,elseL);
        out_.code.push_back({TACKind::Label,"","","","",thenL});
        genBlock(i->thenBlock.get());
        out_.code.push_back({TACKind::Goto,"","","","",endL});
        if(i->elseBlock){out_.code.push_back({TACKind::Label,"","","","",elseL});genBlock(i->elseBlock.get());}
        out_.code.push_back({TACKind::Label,"","","","",endL}); return;
    }
    if(auto w=dynamic_cast<const WhileStmt*>(s)){
        auto head=out_.newLabel("L_while"), body=out_.newLabel("L_body"), end=out_.newLabel("L_end");
        out_.code.push_back({TACKind::Label,"","","","",head});
        genCondition(w->cond.get(),body,end);
        out_.code.push_back({TACKind::Label,"","","","",body});
        genBlock(w->body.get());
        out_.code.push_back({TACKind::Goto,"","","","",head});
        out_.code.push_back({TACKind::Label,"","","","",end}); return;
    }
    throw std::runtime_error("Unknown statement");
}
void TACGenerator::genBlock(const BlockStmt* b){for(const auto& s:b->statements)genStmt(s.get());}
}
