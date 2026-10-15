import { MontoPipe } from './monto.pipe';

describe('MontoPipe', () => {
  const pipe = new MontoPipe();
  const sinEspaciosEspeciales = (texto: string) => texto.replace(/\s/g, ' ');

  it('formatea montos en pesos colombianos', () => {
    expect(sinEspaciosEspeciales(pipe.transform('11521700.00'))).toBe('$ 11.521.700');
    expect(sinEspaciosEspeciales(pipe.transform('1500.50'))).toBe('$ 1.500,5');
    expect(sinEspaciosEspeciales(pipe.transform(-25000))).toBe('-$ 25.000');
  });

  it.each([null, undefined, '', 'abc'])('muestra un guion para %s', (valor) => {
    expect(pipe.transform(valor)).toBe('—');
  });
});
