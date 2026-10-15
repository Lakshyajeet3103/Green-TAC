#pragma once
#include <string>
#include <vector>
#include <cstddef>

namespace greentac {
enum class TokenType {
    Identifier, Number,
    Plus, Minus, Star, Slash, Percent,
    Assign, Eq, Ne, Lt, Le, Gt, Ge,
    LParen, RParen, LBrace, RBrace, Semicolon,
    If, Else, While,
    End
};
struct Token { TokenType type; std::string lexeme; std::size_t line; std::size_t col; };
class Lexer {
public:
    explicit Lexer(std::string source) : source_(std::move(source)) {}
    std::vector<Token> lex() const;
private:
    std::string source_;
};
}
