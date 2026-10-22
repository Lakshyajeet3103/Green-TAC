#include "greentac/steps.h"
#include "greentac/lexer.h"
#include "greentac/parser.h"
#include "greentac/optimizer.h"
#include <iomanip>
#include <sstream>
#include <algorithm>

namespace greentac {
namespace {
struct Tree {
    std::string label;
    std::vector<Tree> children;
};
Tree expression(const Expr* e){
    if(auto n=dynamic_cast<const NumberExpr*>(e)) return {std::to_string(n->value),{}};
    if(auto v=dynamic_cast<const VarExpr*>(e)) return {v->name,{}};
    if(auto b=dynamic_cast<const BinaryExpr*>(e))
        return {b->op,{expression(b->lhs.get()),expression(b->rhs.get())}};
    return {"?",{}};
}
Tree statement(const Stmt* s){
    if(auto a=dynamic_cast<const AssignStmt*>(s)) return {"Assign " + a->name,{expression(a->expr.get())}};
    if(auto b=dynamic_cast<const BlockStmt*>(s)){
        Tree tree{"Block",{}};
        for(const auto& child:b->statements) tree.children.push_back(statement(child.get()));
        return tree;
    }
    if(auto i=dynamic_cast<const IfStmt*>(s)){
        Tree tree{"If",{{"condition:",{expression(i->cond.get())}},
                         {"then:",{statement(i->thenBlock.get())}}}};
        if(i->elseBlock) tree.children.push_back({"else:",{statement(i->elseBlock.get())}});
        return tree;
    }
    if(auto w=dynamic_cast<const WhileStmt*>(s))
        return {"While",{{"condition:",{expression(w->cond.get())}},
                          {"body:",{statement(w->body.get())}}}};
    return {"?",{}};
}
void draw(const Tree& tree, std::ostream& out, const std::string& prefix, bool last){
    out << prefix << (last ? "`-- " : "|-- ") << tree.label << "\n";
    for(std::size_t i=0;i<tree.children.size();++i)
        draw(tree.children[i],out,prefix+(last ? "    " : "|   "),i+1==tree.children.size());
}
void section(std::ostream& out, const std::string& title, const std::string& description){
    out << "\n" << std::string(72,'=') << "\n"
        << title << "\n" << description << "\n" << std::string(72,'-') << "\n";
}
std::vector<std::string> lines(const TACProgram& program){
    std::ostringstream text; program.print(text);
    std::istringstream input(text.str());
    std::vector<std::string> result;
    for(std::string line;std::getline(input,line);) result.push_back(line);
    return result;
}
}
void printCompilationSteps(const std::string& source, std::ostream& out){
    const auto tokens=Lexer(source).lex();
    auto ast=Parser(tokens).parse();
    out << "\nGREEN TAC | COMPILATION WALKTHROUGH\n"
        << "Source -> Tokens -> AST -> TAC -> Simplify -> DAG / CSE\n";
    section(out,"0. Source","The program we will compile.");
    std::istringstream input(source);
    std::size_t lineNumber=0;
    for(std::string line;std::getline(input,line);)
        out << std::right << std::setw(4) << ++lineNumber << " | " << line << "\n";
    if(source.empty()) out << "  (empty program)\n";
    section(out,"1. Tokens","One row per source line. @column marks each token's position.");
    std::size_t currentLine=0;
    for(const auto& token:tokens){
        if(token.type==TokenType::End){ out << "\n  <end>\n"; break; }
        if(token.line!=currentLine){
            if(currentLine) out << "\n";
            currentLine=token.line;
            out << std::right << std::setw(4) << currentLine << " |";
        }
        out << "  " << token.lexeme << " @" << token.col;
    }
    section(out,"2. Abstract syntax tree","Read from the root down; operators connect their operands.");
    out << "Program\n";
    for(std::size_t i=0;i<ast.statements.size();++i)
        draw(statement(ast.statements[i].get()),out,"",i+1==ast.statements.size());
    auto base=TACGenerator().generate(ast);
    section(out,"3. Baseline TAC","Each temporary holds one intermediate computation.");
    auto before=lines(base);
    for(std::size_t i=0;i<before.size();++i)
        out << std::right << std::setw(4) << i+1 << " | " << before[i] << "\n";
    auto final=optimizeWithSteps(base,out);
    section(out,"RESULT | Before and after","Follow each original instruction to its optimized result.");
    const auto after=lines(final);
    std::size_t width=28;
    for(const auto& line:before) width=std::max(width,line.size()+2);
    out << "  " << std::left << std::setw(static_cast<int>(width)) << "BASELINE" << " | DAG OPTIMIZED\n";
    std::size_t next=0;
    for(std::size_t i=0;i<before.size();++i){
        const auto& original=base.code[i];
        bool retained=false;
        if(next<final.code.size()){
            const auto& optimized=final.code[next];
            const bool writesValue=original.kind==TACKind::Assign || original.kind==TACKind::Binary;
            retained=writesValue ? original.result==optimized.result
                                 : original.kind==optimized.kind && original.label==optimized.label;
        }
        out << "  " << std::left << std::setw(static_cast<int>(width)) << before[i]
            << " | " << (retained ? after[next++] : "(eliminated: expression reused)") << "\n";
    }
    out << "\n  Instructions: " << before.size() << " -> " << after.size()
        << "  |  Removed: " << before.size()-after.size() << "\n";
}
}
