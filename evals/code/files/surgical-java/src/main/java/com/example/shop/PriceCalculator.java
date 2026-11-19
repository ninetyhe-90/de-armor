package com.example.shop;

public class PriceCalculator {
    private static final double DISCOUNT_RATE = 0.9;

    public double discount(double price){
        return price*DISCOUNT_RATE;
    }

    private double legacyRound(double v) { return Math.round(v * 100) / 100.0; }
}
