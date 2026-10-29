package com.spe.calculator.model;

/**
 * JSON body returned for a successful calculation, e.g.
 * {"operation":"add","a":2,"b":3,"result":5}.
 */
public record CalculationResponse(String operation, Number a, Number b, Number result) {

    public static CalculationResponse of(String operation, double a, double b, double result) {
        return new CalculationResponse(operation, normalize(a), normalize(b), normalize(result));
    }

    /** Render whole numbers without a trailing ".0" so 2 + 3 returns 5 rather than 5.0. */
    static Number normalize(double value) {
        if (value == Math.rint(value) && Math.abs(value) < 1e15) {
            return (long) value;
        }
        return value;
    }
}
