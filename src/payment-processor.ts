/**
 * payment-processor.ts
 * Senior-level concise example for testing AI documentation agent
 */

export type Currency = "USD" | "EUR" | "INR";

export interface PaymentRequest {
  userId: string;
  amount: number;
  currency: Currency;
}

export interface PaymentResult {
  transactionId: string;
  status: "SUCCESS" | "FAILED";
  processedAt: Date;
}

export interface PaymentGateway {
  charge(request: PaymentRequest): Promise<PaymentResult>;
}

export class PaymentError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PaymentError";
  }
}

export class PaymentProcessor {
  constructor(private readonly gateway: PaymentGateway) {}

  async process(request: PaymentRequest): Promise<PaymentResult> {
    this.validate(request);

    try {
      const result = await this.gateway.charge(request);

      if (result.status === "FAILED") {
        throw new PaymentError("Payment failed at gateway");
      }

      return result;
    } catch (error) {
      throw new PaymentError(
        error instanceof Error ? error.message : "Unknown payment error"
      );
    }
  }

  private validate(request: PaymentRequest): void {
    if (!request.userId) {
      throw new PaymentError("User ID is required");
    }

    if (request.amount <= 0) {
      throw new PaymentError("Amount must be greater than zero");
    }
  }
}