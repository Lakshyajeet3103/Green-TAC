#pragma once
#include <memory>
#include <string>
#include <vector>
#include <utility>

namespace greentac {
struct Expr { virtual ~Expr() = default; };
struct NumberExpr final : Expr { long long value; explicit NumberExpr(long long v):value(v){} };
struct VarExpr final : Expr { std::string name; explicit VarExpr(std::string n):name(std::move(n)){} };
struct BinaryExpr final : Expr { std::string op; std::unique_ptr<Expr> lhs, rhs; BinaryExpr(std::string o,std::unique_ptr<Expr> l,std::unique_ptr<Expr> r):op(std::move(o)),lhs(std::move(l)),rhs(std::move(r)){} };

struct Stmt { virtual ~Stmt() = default; };
struct AssignStmt final : Stmt { std::string name; std::unique_ptr<Expr> expr; AssignStmt(std::string n,std::unique_ptr<Expr> e):name(std::move(n)),expr(std::move(e)){} };
struct BlockStmt final : Stmt { std::vector<std::unique_ptr<Stmt>> statements; };
struct IfStmt final : Stmt { std::unique_ptr<Expr> cond; std::unique_ptr<BlockStmt> thenBlock; std::unique_ptr<BlockStmt> elseBlock; };
struct WhileStmt final : Stmt { std::unique_ptr<Expr> cond; std::unique_ptr<BlockStmt> body; };
struct Program { std::vector<std::unique_ptr<Stmt>> statements; };
}
