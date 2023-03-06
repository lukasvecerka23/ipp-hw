<?php
ini_set('display_errors', 'stderr');
// TODO:
// - Grammar driven syntax parsing
// - Implement each grammar rule 

function exit_error($err_code, $msg){
    fwrite(STDERR, "ERROR: ".$msg."\n");
    exit($err_code);
}

class Parser{
    private $header = false;
    private $opcnt = 1;
    private $xmlwriter;

    public function __construct($xml){
        $this->xmlwriter = $xml;
    }
    public function initXMLWriter(){
        $this->xmlwriter->openMemory();
        $this->xmlwriter->startDocument('1.0', 'UTF-8');
        $this->xmlwriter->setIndent(true);
    }
    public function closeXML(){
        $this->xmlwriter->endDocument();
        fwrite(STDOUT, trim($this->xmlwriter->outputMemory()));
        $this->xmlwriter->flush();
    }

    private function check_write_var($var, $arg){
        if(!preg_match('/^\b(GF|TF|LF)@[_\-$&%\*!\?a-zA-Z][_\-$&%\*!\?a-zA-Z0-9]*$/', $var)){
            exit_error(23, "lexical error, wrong variable name");
        }
        $this->xml_write_operand($var, "var", $arg);
    }
    
    private function check_write_symb($symb, $arg){
        $new_symb = explode("@", $symb, 2);
        if(count($new_symb) != 2) exit_error(23, "invalid symbol");
        switch($new_symb[0]){
            case "string":
                if(!preg_match('/^[^\x00-\x20\x23\x5C]*((\\\\[0-9]{3})[^\x00-\x20\x23\x5C]*)*$/', $new_symb[1])){
                    exit_error(23, "invalid string literal");
                }
                $symb = $new_symb[1];
                $type = "string";
                break;

            case "int":
                if(!preg_match('/^[+|\-]?([1-9][0-9]*|[0-7]+|0[o|O][0-7]+|0[x|X][a-fA-F0-9]+)$/', $new_symb[1])){
                    exit_error(23, "invalid int literal");
                }
                $symb = $new_symb[1];
                $type = "int";
                break;
            case "bool":
                if ($new_symb[1] != "true" && $new_symb[1] != "false"){
                    exit_error(23, "invalid bool literal");
                }
                $symb = $new_symb[1];
                $type = "bool";
                break;
            case "nil":
                if ($new_symb[1] != "nil"){
                    exit_error(23, "invalid nil literal");
                }
                $symb = $new_symb[1];
                $type = "nil";
                break;
            case "GF":
            case "TF":
            case "LF":
                if(!preg_match('/^[_\-$&%\*!\?a-zA-Z][_\-$&%\*!\?a-zA-Z0-9]*$/', $new_symb[1])){
                    exit_error(23, "lexical error in <label>");
                }
                $type = "var";
                break;
            default:
                exit_error(23, "lexical error invalid symbol");
        }
        $this->xml_write_operand($symb, $type, $arg);
    }
    
    private function check_write_label($label, $arg){
        if(!preg_match('/^[_\-$&%\*!\?a-zA-Z][_\-$&%\*!\?a-zA-Z0-9]*$/', $label)){
            exit_error(23, "lexical error in <label>");
        }
        $this->xml_write_operand($label, "label", $arg);
    }
    
    private function check_write_type($type, $arg){
        if(!preg_match('/^(int|bool|string)$/', $type)){
            exit_error(23, "lexical error in <type>");
        }
        $this->xml_write_operand($type, "type", $arg);
    }

    private function xml_write_program(){
        $this->xmlwriter->startElement('program');
        $this->xmlwriter->writeAttribute('language', 'IPPcode23');
    }
    
    private function xml_write_operation($tokens){
        $this->xmlwriter->startElement('instruction');
        $this->xmlwriter->writeAttribute('order', $this->opcnt);
        $this->xmlwriter->writeAttribute('opcode', $tokens[0]);
    }
    
    private function xml_write_operand($operand, $type, $arg){
        $this->xmlwriter->startElement('arg'.$arg);
        $this->xmlwriter->writeAttribute('type', $type);
        $this->xmlwriter->text($operand);
        $this->xmlwriter->endElement();
    }
    
    // operation without operands
    private function nooperands_operation($tokens){
        if (count($tokens) != 1){
            exit_error(23, "Wrong operand count");
        }
        $this->xml_write_operation($tokens);
    }
    
    private function var_operation($tokens){
        if (count($tokens) != 2){
            exit_error(23, "Wrong operand count");
        }
        $this->xml_write_operation($tokens);
        $this->check_write_var($tokens[1], "1");
    }
    
    private function symb_operation($tokens){
        if (count($tokens) != 2){
            exit_error(23, "Wrong operand count");
        }
        $this->xml_write_operation($tokens);
        $this->check_write_symb($tokens[1], "1");
    }
    
    private function label_operation($tokens){
        if (count($tokens) != 2){
            exit_error(23, "Wrong operand count");
        }
        $this->xml_write_operation($tokens);
        $this->check_write_label($tokens[1], "1");
    }
    
    private function var_symb_operation($tokens){
        if (count($tokens) != 3){
            exit_error(23, "Wrong operand count");
        }
        $this-> xml_write_operation($tokens);
        $this->check_write_var($tokens[1], "1");
        $this->check_write_symb($tokens[2], "2");
    }
    
    private function var_type_operation($tokens){
        if (count($tokens) != 3){
            exit_error(23, "Wrong operand count");
        }
        $this->xml_write_operation($tokens);
        $this->check_write_var($tokens[1], "1");
        $this->check_write_type($tokens[2], "2");
    }
    
    private function var_symb1_symb2_operation($tokens){
        if (count($tokens) != 4){
            exit_error(23, "Wrong operand count");
        }
        $this->xml_write_operation($tokens);
        $this->check_write_var($tokens[1], "1");
        $this->check_write_symb($tokens[2], "2");
        $this->check_write_symb($tokens[3], "3");
    }
    
    private function label_symb1_symb2_operation($tokens){
        if (count($tokens) != 4){
            exit_error(23, "Wrong operand count");
        }
        $this->xml_write_operation($tokens);
        $this->check_write_label($tokens[1], "1");
        $this->check_write_symb($tokens[2], "2");
        $this->check_write_symb($tokens[3], "3");
    }

    public function parse_line($line){
        if (!$this->header){
            if($line[0] == ".IPPCODE23" && count($line) == 1){
                $this->xml_write_program();
                $this->header = true;
                return;
            } else {
                exit_error(21, "missing or invalid header .IPPCode23");
            }
        }
        switch($line[0]){
            // without operands
            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                $this->nooperands_operation($line);
                $this->opcnt++;
                break;
            
            // <var>
            case "DEFVAR":
            case "POPS":
                $this->var_operation($line);
                $this->opcnt++;
                break;
    
            // <symb>
            case "PUSHS":
            case "WRITE":
            case "EXIT":
            case "DPRINT":
                $this->symb_operation($line);
                $this->opcnt++;
                break;
    
            // <label>
            case "CALL":
            case "LABEL":
            case "JUMP":
                $this->label_operation($line);
                $this->opcnt++;
                break;
    
            // <var> <symb>
            case "MOVE":
            case "INT2CHAR":
            case "STRLEN":
            case "NOT":
            case "TYPE":
                $this->var_symb_operation($line);
                $this->opcnt++;
                break;
    
            // <var> <type>
            case "READ":
                $this->var_type_operation($line);
                $this->opcnt++;
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
            case "STRI2INT":
            case "CONCAT":
            case "GETCHAR":
            case "SETCHAR":
                $this->var_symb1_symb2_operation($line);
                $this->opcnt++;
                break;
    
            // <label> <symb1> <symb2>
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                $this->label_symb1_symb2_operation($line);
                $this->opcnt++;
                break;
    
            default:
               exit_error(22, "invalid operation code");
        }
        $this->xmlwriter->endElement();
    }
}

// MAIN BODY
if ($argc > 1){
    if ($argv[1] == "--help" && $argc <= 2){
        echo "Help";
        exit(0);
    }
    exit_error(10, "Error in argument parsing");
}

$xml = new XMLWriter();
$parser = new Parser($xml);
$parser->initXMLWriter();

while ($line = fgets(STDIN)){
    // Process each line and split it to tokens
    $line = preg_replace('/#.*/', '', $line); // remove comments
    $line = trim($line);
    if (strlen($line)==0) continue;
    $tokens = preg_split('/\s+/', $line);
    

    $tokens[0] = strtoupper($tokens[0]);
    $parser->parse_line($tokens);
}
$parser->closeXML();

exit(0);
?>