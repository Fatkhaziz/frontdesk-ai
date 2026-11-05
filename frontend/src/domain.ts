export const money = (cents: number) => (cents / 100).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
export const vehicleName = (f: Facts) => `${f.year} ${f.make} ${f.model}`;
export type Facts = {
    make: string;
    model: string;
    year: number;
    price: number;
    mileage: number;
    availability: string;
};
export type Car = {
    id: string;
    revision: number;
    facts: Facts;
    description: string;
    published_revision: number | null;
    published_at?: string | null;
};
export type Config = {
    supabaseUrl: string;
    supabaseKey: string;
    questionMode: 'demo' | 'ai';
    aiEnabled: boolean;
};
export type Api = (path: string, method?: string, body?: unknown) => Promise<any>;
export type Run = (fn: () => Promise<void>) => Promise<void>;
export const blank: Facts = { make: 'Toyota', model: 'Camry', year: 2022, price: 2350000, mileage: 42000, availability: 'available' };
export function dollarsToCents(value: string): number {
    if (!/^\d+(\.\d{1,2})?$/.test(value.trim()))
        throw Error('Enter a price in dollars, with no more than two decimal places.');
    const [dollars, cents = ''] = value.trim().split('.');
    const result = Number(dollars) * 100 + Number(cents.padEnd(2, '0'));
    if (!Number.isSafeInteger(result) || result > 1000000000)
        throw Error('Enter a price between $0 and $10,000,000.');
    return result;
}
export function validateFacts(f: Facts) {
    if (!f.make.trim())
        throw Error('Enter the vehicle make.');
    if (!f.model.trim())
        throw Error('Enter the vehicle model.');
    if (!Number.isInteger(f.year) || f.year < 1886 || f.year > new Date().getFullYear() + 1)
        throw Error('Enter a valid vehicle year.');
    if (!Number.isInteger(f.price) || f.price < 0 || f.price > 1000000000)
        throw Error('Enter a valid price in dollars.');
    if (!Number.isInteger(f.mileage) || f.mileage < 0 || f.mileage > 10000000)
        throw Error('Enter mileage as a whole number between 0 and 10,000,000.');
}
export function sortCars(cars: Car[]) {
    return [...cars].sort((a, b) => Number(b.published_revision !== null) - Number(a.published_revision !== null) || (b.published_at || '').localeCompare(a.published_at || '') || vehicleName(a.facts).localeCompare(vehicleName(b.facts)) || a.id.localeCompare(b.id));
}
export function defaultCar(cars: Car[]) {
    return sortCars(cars).find(c => c.published_revision !== null && c.facts.year === 2022 && c.facts.make.toLowerCase() === 'toyota' && c.facts.model.toLowerCase() === 'camry') || sortCars(cars)[0];
}
export const dateTime = (value?: string) => value ? new Date(value).toLocaleString() : 'No request yet';
