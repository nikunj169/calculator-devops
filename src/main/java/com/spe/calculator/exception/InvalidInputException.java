package com.spe.calculator.exception;

/** Thrown when a request parameter is syntactically a number but not a usable one (NaN, Infinity). */
public class InvalidInputException extends RuntimeException {

    public InvalidInputException(String message) {
        super(message);
    }
}
