class Main inherits IO{
    str: String <-"XYZ";
    main(): Object{
        {
            out_string("A".concat("B\n"));
            out_string(str.concat(str).concat("\n"));
        }
    }; 
};