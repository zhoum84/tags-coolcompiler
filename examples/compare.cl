class Main inherits IO{
    three_int: Int <- 3;
    five_int: Int <- 5;
    main(): Object{
        if three_int < 5 then out_string("3 < 5 is true")
        else
            out_string("3 < 5 is not true")
        fi
    }; 
};