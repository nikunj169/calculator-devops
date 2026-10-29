package com.spe.calculator.model;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class CalculationResponseTest {

    @Test
    void wholeNumbersAreRenderedAsIntegers() {
        assertEquals(5L, CalculationResponse.normalize(5.0));
        assertEquals(-42L, CalculationResponse.normalize(-42.0));
    }

    @Test
    void fractionalNumbersStayDecimal() {
        assertEquals(3.5, CalculationResponse.normalize(3.5));
    }
}
