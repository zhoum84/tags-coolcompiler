class Main inherits IO{

    str: String <-"XYZ";
    alpha4: String<- "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz";
    main(): Object{
        {
            out_int(str.length());
            out_string("\n");
            out_int("abcdefghijklmnopqrstuvwxyz".length());
            out_string("\n");
            out_int((new String).length());
            out_string("\n");
            out_int(alpha4.length());

        }
    }; 
};