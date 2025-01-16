class Main inherits IO{
    lol: Bool <- false;
    main(): Object{
        if lol then out_string("it is true")
        else
            out_string("not true")
        fi
    }; 
};