class Main inherits IO{
    three_int: Int <- 3;
    obj: Object;
    empty: Int;
    main(): Object{{
        if isvoid three_int  then 
            out_string("three_int is void\n")
        else
            out_string("three_int is not void\n")
        fi;
        if not isvoid three_int then 
            out_string("not isvoid three_int is true\n")
        else 
            out_string("not isvoid three_int is false\n")
        fi;
        if isvoid obj then
            out_string("obj is void\n")
        else
            out_string("obj is not void\n") 
        fi;
        if isvoid new Object then
            out_string("new object is void\n")
        else
            out_string("new object is not void\n") 
        fi;
        if isvoid empty then 
            out_string("empty int is void\n")
        else
            out_string("empty int is not void\n") 
        fi;
    }
    }; 
};