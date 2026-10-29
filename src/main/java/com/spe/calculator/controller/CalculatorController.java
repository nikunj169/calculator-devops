package com.spe.calculator.controller;

import com.spe.calculator.exception.InvalidInputException;
import com.spe.calculator.model.CalculationResponse;
import com.spe.calculator.service.CalculatorService;
import java.util.function.DoubleBinaryOperator;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class CalculatorController {

    private final CalculatorService calculator;

    public CalculatorController(CalculatorService calculator) {
        this.calculator = calculator;
    }

    @GetMapping("/add")
    public CalculationResponse add(@RequestParam double a, @RequestParam double b) {
        return calculate("add", a, b, calculator::add);
    }

    @GetMapping("/subtract")
    public CalculationResponse subtract(@RequestParam double a, @RequestParam double b) {
        return calculate("subtract", a, b, calculator::subtract);
    }

    @GetMapping("/multiply")
    public CalculationResponse multiply(@RequestParam double a, @RequestParam double b) {
        return calculate("multiply", a, b, calculator::multiply);
    }

    @GetMapping("/divide")
    public CalculationResponse divide(@RequestParam double a, @RequestParam double b) {
        return calculate("divide", a, b, calculator::divide);
    }

    private CalculationResponse calculate(String operation, double a, double b, DoubleBinaryOperator op) {
        requireFinite("a", a);
        requireFinite("b", b);
        return CalculationResponse.of(operation, a, b, op.applyAsDouble(a, b));
    }

    private static void requireFinite(String name, double value) {
        if (!Double.isFinite(value)) {
            throw new InvalidInputException("Parameter '" + name + "' must be a finite number");
        }
    }
}
