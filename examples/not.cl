class Main inherits IO{
    b: Bool <- false;
    main(): Object{{
        if not b then 
            out_string("not b is true\n")
        else
            out_string("not b is false\n")
        fi;
        if not not b then 
            out_string("not not b is true\n")
        else 
            out_string("not not b is false\n")
        fi;
        if not not not b then 
            out_string("not not not b is true")
        else 
            out_string("not not not b is false")
        fi;

    }
    }; 
};