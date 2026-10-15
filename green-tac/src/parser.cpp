#include "greentac/parser.h"
#include <stdexcept>

namespace greentac {
const Token& Parser::current() const { return tokens_.at(pos_); }
bool Parser::match(TokenType t){ if(current().type==t){++pos_;return true;}return false; }
const Token& Parser::expect(TokenType t,const char* what){ if(current().type!=t) throw std::runtime_error(std::string("Expected ")+what+" at "+std::to_string(current().line)+":"+std::to_string(current().col)); return tokens_[pos_++]; }
Program Parser::parse(){ Program p; while(current().type!=TokenType::End) p.statements.push_back(parseStmt()); return p; }
std::unique_ptr<Stmt> Parser::parseStmt(){
    if(match(TokenType::If)){
        expect(TokenType::LParen,"("); auto cond=parseExpr(); expect(TokenType::RParen,")");
        auto s=std::make_unique<IfStmt>(); s->cond=std::move(cond); s->thenBlock=parseBlock();
        if(match(TokenType::Else)) s->elseBlock=parseBlock();
        return s;
    }
    if(match(TokenType::While)){
        expect(TokenType::LParen,"("); auto cond=parseExpr(); expect(TokenType::RParen,")");
        auto s=std::make_unique<WhileStmt>(); s->cond=std::move(cond); s->body=parseBlock(); return s;
    }
    const auto& id=expect(TokenType::Identifier,"identifier"); expect(TokenType::Assign,"="); auto e=parseExpr(); expect(TokenType::Semicolon,";");
    return std::make_unique<AssignStmt>(id.lexeme,std::move(e));
}
std::unique_ptr<BlockStmt> Parser::parseBlock(){
    expect(TokenType::LBrace,"{"); auto b=std::make_unique<BlockStmt>();
    while(current().type!=TokenType::RBrace){ if(current().type==TokenType::End) throw std::runtime_error("Unterminated block"); b->statements.push_back(parseStmt()); }
    expect(TokenType::RBrace,"}"); return b;
}
std::unique_ptr<Expr> Parser::parseExpr(){ return parseComparison(); }
std::unique_ptr<Expr> Parser::parseComparison(){
    auto e=parseAddSub();
    while(true){ std::string op; switch(current().type){case TokenType::Eq:op="==";break;case TokenType::Ne:op="!=";break;case TokenType::Lt:op="<";break;case TokenType::Le:op="<=";break;case TokenType::Gt:op=">";break;case TokenType::Ge:op=">=";break;default:return e;} ++pos_; auto r=parseAddSub(); e=std::make_unique<BinaryExpr>(op,std::move(e),std::move(r)); }
}
std::unique_ptr<Expr> Parser::parseAddSub(){ auto e=parseMulDiv(); while(current().type==TokenType::Plus||current().type==TokenType::Minus){std::string op=current().lexeme;++pos_;auto r=parseMulDiv();e=std::make_unique<BinaryExpr>(op,std::move(e),std::move(r));}return e; }
std::unique_ptr<Expr> Parser::parseMulDiv(){ auto e=parsePrimary(); while(current().type==TokenType::Star||current().type==TokenType::Slash||current().type==TokenType::Percent){std::string op=current().lexeme;++pos_;auto r=parsePrimary();e=std::make_unique<BinaryExpr>(op,std::move(e),std::move(r));}return e; }
std::unique_ptr<Expr> Parser::parsePrimary(){
    if(match(TokenType::LParen)){auto e=parseExpr();expect(TokenType::RParen,")");return e;}
    if(current().type==TokenType::Number){long long v=std::stoll(current().lexeme);++pos_;return std::make_unique<NumberExpr>(v);}
    if(current().type==TokenType::Identifier){std::string n=current().lexeme;++pos_;return std::make_unique<VarExpr>(std::move(n));}
    throw std::runtime_error("Expected expression at "+std::to_string(current().line)+":"+std::to_string(current().col));
}
}
