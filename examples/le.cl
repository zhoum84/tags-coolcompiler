class Main inherits IO{
    three_int: Int <- 3;
    str: String <-"XYZ";
    main(): Object{
        {    if three_int <= 2 then out_string("3 <= 2 is true\n")
        else
            out_string("3 <= 2 is not true\n")
        fi;
        if "ABC" <= "XYZ" then 
            out_string("ABC <= XYZ is true\n")
        else
            out_string("ABC <= XYZ is not true\n")
        fi;
        if false <= true then 
            out_string("false <= true is true")
        else
            out_string("false <= true is not true")
        fi;
        }
    }; 
};