#include "greentac/lexer.h"
#include <cctype>
#include <stdexcept>

namespace greentac {
std::vector<Token> Lexer::lex() const {
    std::vector<Token> out;
    std::size_t i=0,line=1,col=1;
    auto add=[&](TokenType t,std::string s,std::size_t l,std::size_t c){out.push_back({t,std::move(s),l,c});};
    while(i<source_.size()) {
        char c=source_[i];
        if(c==' '||c=='\t'||c=='\r'){++i;++col;continue;}
        if(c=='\n'){++i;++line;col=1;continue;}
        std::size_t l=line, cc=col;
        if(std::isalpha(static_cast<unsigned char>(c))||c=='_') {
            std::size_t j=i;
            while(j<source_.size()&&(std::isalnum(static_cast<unsigned char>(source_[j]))||source_[j]=='_')) ++j;
            std::string s=source_.substr(i,j-i);
            TokenType t = s=="if"?TokenType::If:s=="else"?TokenType::Else:s=="while"?TokenType::While:TokenType::Identifier;
            add(t,s,l,cc); col += j-i; i=j; continue;
        }
        if(std::isdigit(static_cast<unsigned char>(c))) {
            std::size_t j=i; while(j<source_.size()&&std::isdigit(static_cast<unsigned char>(source_[j]))) ++j;
            add(TokenType::Number,source_.substr(i,j-i),l,cc); col += j-i; i=j; continue;
        }
        auto two=[&](char a,char b,TokenType t)->bool{ if(i+1<source_.size()&&source_[i]==a&&source_[i+1]==b){add(t,source_.substr(i,2),l,cc);i+=2;col+=2;return true;}return false;};
        if(two('=','=',TokenType::Eq)||two('!','=',TokenType::Ne)||two('<','=',TokenType::Le)||two('>','=',TokenType::Ge)) continue;
        TokenType t; bool ok=true;
        switch(c){case '+':t=TokenType::Plus;break;case '-':t=TokenType::Minus;break;case '*':t=TokenType::Star;break;case '/':t=TokenType::Slash;break;case '%':t=TokenType::Percent;break;case '=':t=TokenType::Assign;break;case '<':t=TokenType::Lt;break;case '>':t=TokenType::Gt;break;case '(':t=TokenType::LParen;break;case ')':t=TokenType::RParen;break;case '{':t=TokenType::LBrace;break;case '}':t=TokenType::RBrace;break;case ';':t=TokenType::Semicolon;break;default:ok=false;}
        if(!ok) throw std::runtime_error("Unexpected character at "+std::to_string(l)+":"+std::to_string(cc));
        add(t,std::string(1,c),l,cc); ++i;++col;
    }
    out.push_back({TokenType::End,"",line,col}); return out;
}
}
