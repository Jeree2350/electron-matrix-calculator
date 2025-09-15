import json
import numpy as np
from fractions import Fraction
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime

app = Flask(__name__)
CORS(app)

class MatrixCalculator:
    def __init__(self):
        self.history_file = 'matrix_history.json'
        self.settings_file = 'app_settings.json'
        self.load_settings()
    
    def load_settings(self):
        """Cargar configuraciones guardadas"""
        default_settings = {
            'theme': 'light',
            'primary_color': '#007bff',
            'font_size': 14,
            'font_family': 'Arial',
            'decimal_places': 4,
            'show_fractions': True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = default_settings
                self.save_settings()
        except:
            self.settings = default_settings
    
    def save_settings(self):
        """Guardar configuraciones"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuraciones: {e}")
    
    def decimal_to_fraction(self, decimal_num):
        """Convertir decimal a fracción si es necesario"""
        if abs(decimal_num - round(decimal_num)) < 1e-10:
            return str(int(round(decimal_num)))
        
        frac = Fraction(decimal_num).limit_denominator(1000)
        if abs(float(frac) - decimal_num) < 1e-10:
            return str(frac)
        return f"{decimal_num:.{self.settings['decimal_places']}f}"
    
    def format_matrix_display(self, matrix):
        """Formatear matriz para mostrar"""
        formatted = []
        for row in matrix:
            formatted_row = []
            for element in row:
                if self.settings['show_fractions']:
                    formatted_row.append(self.decimal_to_fraction(float(element)))
                else:
                    formatted_row.append(f"{float(element):.{self.settings['decimal_places']}f}")
            formatted.append(formatted_row)
        return formatted
    
    def save_to_history(self, operation, matrices, result, steps):
        """Guardar operación en el historial"""
        history_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'operation': operation,
            'matrices': matrices,
            'result': result,
            'steps': steps
        }
        
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.insert(0, history_entry)  # Más reciente primero
            
            # Mantener solo los últimos 50 registros
            if len(history) > 50:
                history = history[:50]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error guardando historial: {e}")
    
    def get_history(self):
        """Obtener historial"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def matrix_addition(self, matrix_a, matrix_b):
        """Suma de matrices con pasos"""
        try:
            a = np.array(matrix_a, dtype=float)
            b = np.array(matrix_b, dtype=float)
            
            if a.shape != b.shape:
                return {
                    'success': False,
                    'error': 'Las matrices deben tener las mismas dimensiones para sumar'
                }
            
            result = a + b
            
            steps = [
                f"Suma de matrices {a.shape[0]}x{a.shape[1]}",
                "Matriz A:",
                self.format_matrix_display(a.tolist()),
                "Matriz B:",
                self.format_matrix_display(b.tolist()),
                "Procedimiento: C[i,j] = A[i,j] + B[i,j]",
                "Resultado:"
            ]
            
            formatted_result = self.format_matrix_display(result.tolist())
            
            self.save_to_history('suma', {
                'matrix_a': self.format_matrix_display(a.tolist()),
                'matrix_b': self.format_matrix_display(b.tolist())
            }, formatted_result, steps)
            
            return {
                'success': True,
                'result': formatted_result,
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def matrix_subtraction(self, matrix_a, matrix_b):
        """Resta de matrices con pasos"""
        try:
            a = np.array(matrix_a, dtype=float)
            b = np.array(matrix_b, dtype=float)
            
            if a.shape != b.shape:
                return {
                    'success': False,
                    'error': 'Las matrices deben tener las mismas dimensiones para restar'
                }
            
            result = a - b
            
            steps = [
                f"Resta de matrices {a.shape[0]}x{a.shape[1]}",
                "Matriz A:",
                self.format_matrix_display(a.tolist()),
                "Matriz B:",
                self.format_matrix_display(b.tolist()),
                "Procedimiento: C[i,j] = A[i,j] - B[i,j]",
                "Resultado:"
            ]
            
            formatted_result = self.format_matrix_display(result.tolist())
            
            self.save_to_history('resta', {
                'matrix_a': self.format_matrix_display(a.tolist()),
                'matrix_b': self.format_matrix_display(b.tolist())
            }, formatted_result, steps)
            
            return {
                'success': True,
                'result': formatted_result,
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def matrix_multiplication(self, matrix_a, matrix_b):
        """Multiplicación de matrices con pasos"""
        try:
            a = np.array(matrix_a, dtype=float)
            b = np.array(matrix_b, dtype=float)
            
            if a.shape[1] != b.shape[0]:
                return {
                    'success': False,
                    'error': 'El número de columnas de A debe ser igual al número de filas de B'
                }
            
            result = np.dot(a, b)
            
            steps = [
                f"Multiplicación de matrices {a.shape[0]}x{a.shape[1]} × {b.shape[0]}x{b.shape[1]}",
                "Matriz A:",
                self.format_matrix_display(a.tolist()),
                "Matriz B:",
                self.format_matrix_display(b.tolist()),
                "Procedimiento: C[i,j] = Σ(A[i,k] × B[k,j])",
            ]
            
            # Mostrar algunos cálculos detallados para matrices pequeñas
            if a.shape[0] <= 3 and b.shape[1] <= 3:
                steps.append("Cálculos detallados:")
                for i in range(min(2, result.shape[0])):
                    for j in range(min(2, result.shape[1])):
                        calculation = []
                        for k in range(a.shape[1]):
                            calculation.append(f"({self.decimal_to_fraction(a[i,k])}×{self.decimal_to_fraction(b[k,j])})")
                        steps.append(f"C[{i},{j}] = {' + '.join(calculation)} = {self.decimal_to_fraction(result[i,j])}")
            
            steps.append("Resultado:")
            
            formatted_result = self.format_matrix_display(result.tolist())
            
            self.save_to_history('multiplicacion', {
                'matrix_a': self.format_matrix_display(a.tolist()),
                'matrix_b': self.format_matrix_display(b.tolist())
            }, formatted_result, steps)
            
            return {
                'success': True,
                'result': formatted_result,
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def matrix_determinant(self, matrix_a):
        """Determinante de matriz con pasos"""
        try:
            a = np.array(matrix_a, dtype=float)
            
            if a.shape[0] != a.shape[1]:
                return {
                    'success': False,
                    'error': 'La matriz debe ser cuadrada para calcular el determinante'
                }
            
            det = np.linalg.det(a)
            
            steps = [
                f"Determinante de matriz {a.shape[0]}x{a.shape[1]}",
                "Matriz A:",
                self.format_matrix_display(a.tolist())
            ]
            
            if a.shape[0] == 1:
                steps.append(f"Para matriz 1x1: det(A) = {self.decimal_to_fraction(a[0,0])}")
            elif a.shape[0] == 2:
                steps.append("Para matriz 2x2: det(A) = ad - bc")
                steps.append(f"det(A) = ({self.decimal_to_fraction(a[0,0])})×({self.decimal_to_fraction(a[1,1])}) - ({self.decimal_to_fraction(a[0,1])})×({self.decimal_to_fraction(a[1,0])})")
                steps.append(f"det(A) = {self.decimal_to_fraction(a[0,0]*a[1,1])} - {self.decimal_to_fraction(a[0,1]*a[1,0])}")
            elif a.shape[0] == 3:
                steps.append("Para matriz 3x3 usando la regla de Sarrus:")
                steps.append("det(A) = a₁₁(a₂₂a₃₃ - a₂₃a₃₂) - a₁₂(a₂₁a₃₃ - a₂₃a₃₁) + a₁₃(a₂₁a₃₂ - a₂₂a₃₁)")
                
                term1 = a[0,0] * (a[1,1]*a[2,2] - a[1,2]*a[2,1])
                term2 = a[0,1] * (a[1,0]*a[2,2] - a[1,2]*a[2,0])
                term3 = a[0,2] * (a[1,0]*a[2,1] - a[1,1]*a[2,0])
                
                steps.append(f"= {self.decimal_to_fraction(a[0,0])}×({self.decimal_to_fraction(term1/a[0,0])}) - {self.decimal_to_fraction(a[0,1])}×({self.decimal_to_fraction(term2/a[0,1])}) + {self.decimal_to_fraction(a[0,2])}×({self.decimal_to_fraction(term3/a[0,2])})")
                steps.append(f"= {self.decimal_to_fraction(term1)} - {self.decimal_to_fraction(term2)} + {self.decimal_to_fraction(term3)}")
            else:
                steps.append("Para matrices mayores a 3x3 se usa expansión de cofactores")
            
            steps.append(f"Determinante = {self.decimal_to_fraction(det)}")
            
            self.save_to_history('determinante', {
                'matrix_a': self.format_matrix_display(a.tolist())
            }, self.decimal_to_fraction(det), steps)
            
            return {
                'success': True,
                'result': self.decimal_to_fraction(det),
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def matrix_transpose(self, matrix_a):
        """Transpuesta de matriz con pasos"""
        try:
            a = np.array(matrix_a, dtype=float)
            result = a.T
            
            steps = [
                f"Transpuesta de matriz {a.shape[0]}x{a.shape[1]}",
                "Matriz A:",
                self.format_matrix_display(a.tolist()),
                "Procedimiento: A^T[i,j] = A[j,i]",
                "La transpuesta intercambia filas por columnas",
                "Resultado:"
            ]
            
            formatted_result = self.format_matrix_display(result.tolist())
            
            self.save_to_history('transpuesta', {
                'matrix_a': self.format_matrix_display(a.tolist())
            }, formatted_result, steps)
            
            return {
                'success': True,
                'result': formatted_result,
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def matrix_inverse(self, matrix_a):
        """Inversa de matriz con pasos"""
        try:
            a = np.array(matrix_a, dtype=float)
            
            if a.shape[0] != a.shape[1]:
                return {
                    'success': False,
                    'error': 'La matriz debe ser cuadrada para calcular la inversa'
                }
            
            det = np.linalg.det(a)
            if abs(det) < 1e-10:
                return {
                    'success': False,
                    'error': 'La matriz no es invertible (determinante = 0)'
                }
            
            result = np.linalg.inv(a)
            
            steps = [
                f"Inversa de matriz {a.shape[0]}x{a.shape[1]}",
                "Matriz A:",
                self.format_matrix_display(a.tolist()),
                f"Determinante = {self.decimal_to_fraction(det)}",
                "Como det(A) ≠ 0, la matriz es invertible"
            ]
            
            if a.shape[0] == 2:
                steps.append("Para matriz 2x2: A⁻¹ = (1/det(A)) × [d -b; -c a]")
                adj_matrix = np.array([[a[1,1], -a[0,1]], [-a[1,0], a[0,0]]])
                steps.append("Matriz adjunta:")
                steps.append(self.format_matrix_display(adj_matrix.tolist()))
                steps.append(f"A⁻¹ = (1/{self.decimal_to_fraction(det)}) × matriz adjunta")
            else:
                steps.append("Para matrices mayores se usa el método de Gauss-Jordan")
                steps.append("o la fórmula A⁻¹ = (1/det(A)) × adj(A)")
            
            steps.append("Resultado:")
            
            formatted_result = self.format_matrix_display(result.tolist())
            
            self.save_to_history('inversa', {
                'matrix_a': self.format_matrix_display(a.tolist())
            }, formatted_result, steps)
            
            return {
                'success': True,
                'result': formatted_result,
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Instancia del calculador
calculator = MatrixCalculator()

# Rutas de la API
@app.route('/api/suma', methods=['POST'])
def api_suma():
    data = request.json
    return jsonify(calculator.matrix_addition(data['matrix_a'], data['matrix_b']))

@app.route('/api/resta', methods=['POST'])
def api_resta():
    data = request.json
    return jsonify(calculator.matrix_subtraction(data['matrix_a'], data['matrix_b']))

@app.route('/api/multiplicacion', methods=['POST'])
def api_multiplicacion():
    data = request.json
    return jsonify(calculator.matrix_multiplication(data['matrix_a'], data['matrix_b']))

@app.route('/api/determinante', methods=['POST'])
def api_determinante():
    data = request.json
    return jsonify(calculator.matrix_determinant(data['matrix']))

@app.route('/api/transpuesta', methods=['POST'])
def api_transpuesta():
    data = request.json
    return jsonify(calculator.matrix_transpose(data['matrix']))

@app.route('/api/inversa', methods=['POST'])
def api_inversa():
    data = request.json
    return jsonify(calculator.matrix_inverse(data['matrix']))

@app.route('/api/historial', methods=['GET'])
def api_historial():
    return jsonify(calculator.get_history())

@app.route('/api/configuracion', methods=['GET'])
def api_get_configuracion():
    return jsonify(calculator.settings)

@app.route('/api/configuracion', methods=['POST'])
def api_save_configuracion():
    data = request.json
    calculator.settings.update(data)
    calculator.save_settings()
    return jsonify({'success': True})

@app.route('/api/limpiar-historial', methods=['POST'])
def api_limpiar_historial():
    try:
        if os.path.exists(calculator.history_file):
            os.remove(calculator.history_file)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)