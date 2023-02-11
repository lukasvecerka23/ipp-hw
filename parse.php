<?php
ini_set('display_errors', 'stderr');
// TODO:
// - Grammar driven syntax parsing
// - Implement each grammar rule 

function exit_error($err_code, $msg){
    fwrite(STDERR, "ERROR: ".$msg."\n");
    exit($err_code);
}

function xml_write_program($xmlwriter){
    $xmlwriter->startElement('program');
    $xmlwriter->writeAttribute('language', 'IPPcode23');
}

function xml_write_operation($xmlwriter, $tokens, $opcnt){
    $xmlwriter->startElement('instruction');
    $xmlwriter->writeAttribute('order', $opcnt);
    $xmlwriter->writeAttribute('opcode', $tokens[0]);
}

function xml_write_operand($xmlwriter, $operand, $type, $arg){
    $xmlwriter->startElement('arg'.$arg);
    $xmlwriter->writeAttribute('type', $type);
    $xmlwriter->text($operand);
    $xmlwriter->endElement();
}

// operation without operands
function nooperands_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 1){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
}

function var_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 2){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
    check_write_var($xmlwriter, $tokens[1], "1");
}

function symb_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 2){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
    check_write_symb($xmlwriter, $tokens[1], "1");
}

function label_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 2){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
    check_write_label($xmlwriter, $tokens[1], "1");
}

function var_symb_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 3){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
    check_write_var($xmlwriter, $tokens[1], "1");
    check_write_symb($xmlwriter, $tokens[2], "2");
}

function var_type_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 3){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
    check_write_var($xmlwriter, $tokens[1], "1");
    check_write_type($xmlwriter, $tokens[2], "2");
}

function var_symb1_symb2_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 4){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
    check_write_var($xmlwriter, $tokens[1], "1");
    check_write_symb($xmlwriter, $tokens[2], "2");
    check_write_symb($xmlwriter, $tokens[3], "3");
}

function label_symb1_symb2_operation($xmlwriter, $tokens, $opcnt){
    if (count($tokens) != 4){
        print_error(23, "Wrong operand count");
    }
    xml_write_operation($xmlwriter, $tokens, $opcnt);
    check_write_label($xmlwriter, $tokens[1], "1");
    check_write_symb($xmlwriter, $tokens[2], "2");
    check_write_symb($xmlwriter, $tokens[3], "3");
}

function check_write_var($xmlwriter, $var, $arg){
    // lexical check
    xml_write_operand($xmlwriter, $var, "var", $arg);
}

function check_write_symb($xmlwriter, $symb, $arg){
    // lexical check
    xml_write_operand($xmlwriter, $symb, "symb", $arg);
}

function check_write_label($xmlwriter, $label, $arg){
    // lexical check
    xml_write_operand($xmlwriter, $label, "label", $arg);
}

function check_write_type($xmlwriter, $type, $arg){
    // lexical check
    xml_write_operand($xmlwriter, $type, "type", $arg);
}

if ($argc > 1){
    if ($argv[1] == "--help" && $argc <= 2){
        echo "Help";
        exit(0);
    }
    exit_error(10, "Error in argument parsing");
}

$header = false;
$opcnt = 1;

$xmlwriter = new XMLWriter();
$xmlwriter->openMemory();
$xmlwriter->startDocument('1.0', 'UTF-8');
$xmlwriter->setIndent(true);


while ($line = fgets(STDIN)){
    // Process each line and split it to tokens
    $line = preg_replace('/#.*/', '', $line); // remove comments
    $line = trim($line);
    $tokens = preg_split('/\s+/', $line);

    $tokens[0] = strtoupper($tokens[0]);

    if (!$header){
        if($tokens[0] == ".IPPCODE23" && count($tokens) == 1){
            xml_write_program($xmlwriter);
            $header = true;
            continue;
        } else {
            exit_error(21, "missing or invalid header .IPPCode23");
        }
    }

    switch($tokens[0]){
        // without operands
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            nooperands_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
            break;
        
        // <var>
        case "DEFVAR":
        case "POPS":
            var_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
            break;

        // <symb>
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            symb_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
            break;

        // <label>
        case "CALL":
        case "LABEL":
        case "JUMP":
            label_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
            break;

        // <var> <symb>
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
            var_symb_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
            break;

        // <var> <type>
        case "READ":
            var_type_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
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
            var_symb1_symb2_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
            break;

        // <label> <symb1> <symb2>
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            label_symb1_symb2_operation($xmlwriter, $tokens, $opcnt);
            $opcnt++;
            break;

        default:
           exit_error(22, "invalid operation code");
    }
    $xmlwriter->endElement();
}
$xmlwriter->endDocument();
fwrite(STDOUT, trim($xmlwriter->outputMemory()));
$xmlwriter->flush();
?>