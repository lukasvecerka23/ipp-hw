<?php
ini_set('display_errors', 'stderr');
// TODO:
// - Parser header
// - Grammar driven syntax parsing
// - Implement each grammar rule 

if ($argc > 1){
    if ($argv[1] == "--help" && $argc <= 2){
        echo "Help";
        exit(0);
    }
    fwrite(STDERR, "Error in argument parsing");
    exit(10);
}

$header = false;

while ($line = fgets(STDIN)){
    $opcnt = 0;
    // Process each line and split it to tokens
    $line = trim($line);
    $line = preg_replace('/#.*/', '', $line); // remove comments
    $tokens = preg_split('/\s+/', $line);
    print_r($tokens);

    $tokens[0] = strtoupper($tokens[0]);

    if (!$header){
        if($tokens[0] == ".IPPCODE23"){
            echo "Header ok";
            $header = true;
            continue;
        } else {
            fwrite(STDERR, "missing header file");
        }
    }

    switch($tokens[0]){
        // without operands
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            echo "OP without operands";
            break;
        
        // <var>
        case "DEFVAR":
        case "POPS":
            echo "<var> OP";
            break;

        // <symb>
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            echo "<symb> OP";
            break;

        // <label>
        case "CALL":
        case "LABEL":
        case "JUMP":
            echo "<label> OP";
            break;

        // <var> <symb>
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
            echo "<var> <symb> OP";
            break;

        // <var> <type>
        case "READ":
            echo "<var> <type> OP";
            break;

        // <var> <symb1> <symb2>
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "NOT":
        case "STR2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
            echo "<var> <symb1> <symb2> OP";
            break;

        // <label> <symb1> <symb2>
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            echo "<label> <symb1> <symb2> OP";
            break;

        default:
            fwrite(STDERR, "invalid opcode");
            exit(23);
    }
}
?>