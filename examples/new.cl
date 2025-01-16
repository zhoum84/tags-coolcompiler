class Main inherits IO{
    new_int: Int <- new Int;
    new_string: String <- new String;
    main(): Object{{
        out_int(new_int);
        out_string("new_string: ");
        out_string(new_string);
    }
    }; 
};