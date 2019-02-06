Loteos interpreter  
  
All information presented is from the personal understanding and supporting documents.  
Feel free to make a pull request if there is anything I've misinterpreted - contributing to the project in any way is encouraged.  
  
  
 Install (Python 3.6)  
```  
pip install loteos_interpreter  
```  
  
  
-----  
  
 Contents  
1. [Introduction](introduction)  
2. [Usage](usage)  
  
-----  
  
 Introduction  
> Interpreter for Loteos language using Python.  

Loteos labguage is imperative dynamically typed.

The goal of this document is to extensively document the system and implement it.  
  
  
-----  
  
 Usage/Syntax
write here for more example usage.  
  
```
 program     -> declaration* EOF ;  
   
 declaration -> funDecl  
             | varDecl  
             | statement  
             | lotoesCommand;  
   
 funDecl  -> "fun" function ;  
 function -> IDENTIFIER "(" parameters? ")" block ;  
 parameters -> IDENTIFIER ( "," IDENTIFIER )* ;  
  
 lotoesCommand -> assert | command  
 asser -> "assert" "(" command, consistency_level ")" ;  
 command -> read | write | remove | lock | unlock  
 read -> READ "(" primary ")" ;  
 write -> WRITE "(" primary "," primary ")" ;  
 remove -> REMOVE "(" primary ")" ;  
 lock -> LOCK "(" primary ")" ;  
 unlock -> UNLOCK "(" primary ")" ;  
  
 consistency_level -> SC | EC | MC ;  
  
  
 statement  -> exprStmt  
            | forStmt  
            | ifStmt  
            | printStmt  
            | returnStmt  
            | whileStmt  
            | block ;  
 returnStmt -> "return" expression? ";" ;  
  
  
 forStmt   -> "for" "(" ( varDecl | exprStmt | ";" )  
                       expression? ";"  
                       expression? ")" statement ;  
 varDecl -> "var" IDENTIFIER ( "=" expression | read )? ";" ;  
  
 whileStmt -> "while" "(" expression ")" statement ;  
  
 ifStmt    -> "if" "(" expression ")" statement ( "else" statement )? ;  
  
 block     -> "{" declaration* "}" ;  
  
 exprStmt  -> expression ";" ;  
 printStmt -> "print" expression "  
  
  
 expression -> assignment ;  
 assignment -> identifier "=" assignment | read  
            | logic_or ;  
 logic_or   -> logic_and ( "or" logic_and )* ;  
 logic_and  -> equality ( "and" equality )* ;  
  
 equality       -> comparison ( ( "!=" | "==" ) comparison )* ;  
 comparison     -> addition ( ( ">" | ">=" | "<" | "<=" ) addition )* ;  
 addition       -> multiplication ( ( "-" | "+" ) multiplication )* ;  
 multiplication -> unary ( ( "/" | "*" ) unary )* ;  
  
 unary -> ( "!" | "-" ) unary | call ;  
 call  -> primary ( "(" arguments? ")" )* ;  
 arguments -> expression ( "," expression )* ;  
  
                | primary ;  
 primary        -> NUMBER | STRING | "false" | "true" | "nil"  
                | "(" expression ")"  | IDENTIFIER ;  
```  
  
-----  
  
-----  
  
Project by Nabil M. Al-Rousan.  
nabil @ ece.ubc.ca
