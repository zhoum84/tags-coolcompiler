class Main inherits IO{
    three_int: Int <- 3;
    main(): Object{{
        -- out_int(~three_int);
        if ~ three_int < 0 then 
            out_string("not three_int is true\n")
        else
            out_string("not three_int is false\n")
        fi;
        if ~ ~three_int < 0 then 
            out_string("not not three_int is true\n")
        else 
            out_string("not not three_int is false\n")
        fi;
        if ~ ~ ~ three_int < 0 then 
            out_string("not not not three_int is true")
        else 
            out_string("not not not three_int is false")
        fi;

    }
    }; 
};