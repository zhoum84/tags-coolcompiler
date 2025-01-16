class Main inherits IO{
    three_int: Int <- 3;
    other_string: String <- "AB";
    main(): Object{{
        if three_int = 2 + 1 then out_string("3 = 3 is true\n")
        else
            out_string("3 = 3 is not true")
        fi;
        if "ABC" = other_string.concat("C") then out_string("ABC = ABC is true\n")
        else
            out_string("ABC = ABC is not true")
        fi;
        if true = false then out_string("true = true is true")
        else
            out_string("true = true is not true")
        fi;
    }
    }; 
};