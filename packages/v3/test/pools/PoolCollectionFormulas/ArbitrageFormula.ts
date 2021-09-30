import { expect } from 'chai';
import Contracts from '../../../components/Contracts';
import { TestArbitrageFormula } from '../../../typechain';
import fs from 'fs';
import path from 'path';
import { BigNumber } from 'ethers';
import Decimal from 'decimal.js';

describe('ArbitrageFormula', () => {
    let formula: TestArbitrageFormula;

    before(async () => {
        formula = await Contracts.TestArbitrageFormula.deploy();
    });

    describe('tests', () => {
        interface Row {
            a: string;
            b: string;
            c: string;
            e: string;
            m: string;
            n: string;
            x: string;
            p: string;
            q: string;
            r: string;
            s: string;
        }

        interface MaxError {
            absolute: Decimal;
            relative: Decimal;
        }

        interface MaxErrors {
            p: MaxError;
            q: MaxError;
            r: MaxError;
            s: MaxError;
        }

        const tests = (numOfTestsPerFile: number = Number.MAX_SAFE_INTEGER) => {
            const test = (fileName: string, maxErrors: MaxErrors) => {
                const table: Row[] = JSON.parse(
                    fs.readFileSync(path.join(__dirname, '../../data', `${fileName}.json`), { encoding: 'utf8' })
                ).slice(0, numOfTestsPerFile);

                for (const {a, b, c, e, m, n, x, p, q, r, s} of table) {
                    if (BigNumber.from(b).add(BigNumber.from(c)).gte(BigNumber.from(e))) {
                        it(`${fileName} surplus(${[a, b, c, e, m, n, x]})`, async () => {
                            const actual = await formula.surplus(a, b, c, e, m, n, x);
                            expect(actual.p).to.almostEqual(new Decimal(p), maxErrors.p.absolute, maxErrors.p.relative);
                            expect(actual.q).to.almostEqual(new Decimal(q), maxErrors.q.absolute, maxErrors.q.relative);
                            expect(actual.r).to.almostEqual(new Decimal(r), maxErrors.r.absolute, maxErrors.r.relative);
                            expect(actual.s).to.almostEqual(new Decimal(s), maxErrors.s.absolute, maxErrors.s.relative);
                        });
                    }
                    else {
                        it(`${fileName} deficit(${[a, b, c, e, m, n, x]})`, async () => {
                            const actual = await formula.deficit(a, b, c, e, m, n, x);
                            expect(actual.p).to.almostEqual(new Decimal(p), maxErrors.p.absolute, maxErrors.p.relative);
                            expect(actual.q).to.almostEqual(new Decimal(q), maxErrors.q.absolute, maxErrors.q.relative);
                            expect(actual.r).to.almostEqual(new Decimal(r), maxErrors.r.absolute, maxErrors.r.relative);
                            expect(actual.s).to.almostEqual(new Decimal(s), maxErrors.s.absolute, maxErrors.s.relative);
                        });
                    }
                }
            };

            test(
                'ArbitrageFormulaCoverage1', {
                    p: { absolute: new Decimal(1), relative: new Decimal('0.0000004') },
                    q: { absolute: new Decimal(1), relative: new Decimal('0.0000004') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0') },
                }
            );

            test(
                'ArbitrageFormulaCoverage2', {
                    p: { absolute: new Decimal(1), relative: new Decimal('0.00000000000000005') },
                    q: { absolute: new Decimal(1), relative: new Decimal('0.00000000000000009') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0') },
                }
            );

            test(
                'ArbitrageFormulaCoverage3', {
                    p: { absolute: new Decimal(1), relative: new Decimal('0.0000000000000000003') },
                    q: { absolute: new Decimal(1), relative: new Decimal('0.0000000000000000002') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0') },
                }
            );

            test(
                'ArbitrageFormulaCoverage4', {
                    p: { absolute: new Decimal(1), relative: new Decimal('0.003') },
                    q: { absolute: new Decimal(2), relative: new Decimal('0.002') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0') },
                }
            );

            test(
                'ArbitrageFormulaCoverage5', {
                    p: { absolute: new Decimal(1), relative: new Decimal('0.00002') },
                    q: { absolute: new Decimal(1), relative: new Decimal('0.000007') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0') },
                }
            );

            test(
                'ArbitrageFormulaCoverage6', {
                    p: { absolute: new Decimal(1), relative: new Decimal('0.00000000005') },
                    q: { absolute: new Decimal(1), relative: new Decimal('0.00000000005') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0') },
                }
            );

            test(
                'ArbitrageFormulaCoverage7', {
                    p: { absolute: new Decimal(1), relative: new Decimal('0.000002') },
                    q: { absolute: new Decimal(1), relative: new Decimal('0.000003') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0') },
                }
            );

            test(
                'ArbitrageFormulaCoverage8', {
                    p: { absolute: new Decimal(2), relative: new Decimal('0.009') },
                    q: { absolute: new Decimal(2), relative: new Decimal('0.009') },
                    r: { absolute: new Decimal(1), relative: new Decimal('0.00000003') },
                    s: { absolute: new Decimal(1), relative: new Decimal('0.00000003') },
                }
            );
        };

        describe('quick tests', () => {
            tests(100);
        });

        describe('@stress tests', () => {
            tests();
        });
    });
});
