package com.spe.calculator.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class CalculatorServiceTest {

    private static final double DELTA = 1e-9;

    private final CalculatorService calculator = new CalculatorService();

    @ParameterizedTest(name = "{0} + {1} = {2}")
    @CsvSource({"2, 3, 5", "-4, 1.5, -2.5", "0, 0, 0", "1e10, 1e10, 2e10"})
    void addReturnsSum(double a, double b, double expected) {
        assertEquals(expected, calculator.add(a, b), DELTA);
    }

    @ParameterizedTest(name = "{0} - {1} = {2}")
    @CsvSource({"10, 4, 6", "4, 10, -6", "-3, -3, 0", "2.5, 0.5, 2"})
    void subtractReturnsDifference(double a, double b, double expected) {
        assertEquals(expected, calculator.subtract(a, b), DELTA);
    }

    @ParameterizedTest(name = "{0} * {1} = {2}")
    @CsvSource({"6, 7, 42", "-2, 3, -6", "5, 0, 0", "1.5, 1.5, 2.25"})
    void multiplyReturnsProduct(double a, double b, double expected) {
        assertEquals(expected, calculator.multiply(a, b), DELTA);
    }

    @ParameterizedTest(name = "{0} / {1} = {2}")
    @CsvSource({"10, 2, 5", "7, 2, 3.5", "-9, 3, -3", "0, 5, 0"})
    void divideReturnsQuotient(double a, double b, double expected) {
        assertEquals(expected, calculator.divide(a, b), DELTA);
    }

    @Test
    @DisplayName("divide by zero throws ArithmeticException")
    void divideByZeroThrows() {
        ArithmeticException ex = assertThrows(ArithmeticException.class, () -> calculator.divide(5, 0));
        assertEquals("Division by zero is not allowed", ex.getMessage());
    }

    @Test
    @DisplayName("divide zero by zero also throws")
    void divideZeroByZeroThrows() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(0, 0));
    }
}
