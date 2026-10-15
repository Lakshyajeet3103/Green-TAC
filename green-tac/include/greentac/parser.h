#pragma once
#include "greentac/ast.h"
#include "greentac/lexer.h"
#include <string>
#include <vector>

namespace greentac {
class Parser {
public:
    explicit Parser(std::vector<Token> tokens) : tokens_(std::move(tokens)) {}
    Program parse();
private:
    const Token& current() const;
    bool match(TokenType t);
    const Token& expect(TokenType t, const char* what);
    std::unique_ptr<Stmt> parseStmt();
    std::unique_ptr<BlockStmt> parseBlock();
    std::unique_ptr<Expr> parseExpr();
    std::unique_ptr<Expr> parseComparison();
    std::unique_ptr<Expr> parseAddSub();
    std::unique_ptr<Expr> parseMulDiv();
    std::unique_ptr<Expr> parsePrimary();
    std::vector<Token> tokens_; std::size_t pos_{0};
};
}
