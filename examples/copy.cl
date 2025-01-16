class Main inherits IO{
    lol: Int <- 100;
    bruh: Int <- lol.copy();
    s: String <- "hello";
    t: String <- s.copy();

    main(): Object{{
        out_int(bruh);
        out_string("\n");
        out_string(t);
--        out_string(other2.t);
    }
    };
};
