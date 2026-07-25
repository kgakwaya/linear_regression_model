import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'African Life Expectancy Predictor',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const LifeExpectancyPredictorPage(),
    );
  }
}

class LifeExpectancyPredictorPage extends StatefulWidget {
  const LifeExpectancyPredictorPage({super.key});

  @override
  State<LifeExpectancyPredictorPage> createState() =>
      _LifeExpectancyPredictorPageState();
}

class _LifeExpectancyPredictorPageState extends State<LifeExpectancyPredictorPage> {
  // API endpoint (update with your Render URL after deployment)
  final String apiUrl = 'http://localhost:8000/predict';

  // Text controllers
  final TextEditingController adultMortalityController = TextEditingController();
  final TextEditingController infantDeathsController = TextEditingController();
  final TextEditingController bmiController = TextEditingController();
  final TextEditingController gdpController = TextEditingController();
  final TextEditingController schoolingController = TextEditingController();

  // State variables
  bool isLoading = false;
  String resultMessage = '';
  Color resultColor = Colors.grey;

  @override
  void dispose() {
    adultMortalityController.dispose();
    infantDeathsController.dispose();
    bmiController.dispose();
    gdpController.dispose();
    schoolingController.dispose();
    super.dispose();
  }

  // Validate input fields
  bool validateInputs() {
    if (adultMortalityController.text.isEmpty ||
        infantDeathsController.text.isEmpty ||
        bmiController.text.isEmpty ||
        gdpController.text.isEmpty ||
        schoolingController.text.isEmpty) {
      setState(() {
        resultMessage = 'Error: All fields are required!';
        resultColor = Colors.red;
      });
      return false;
    }

    try {
      double adultMortality = double.parse(adultMortalityController.text);
      int infantDeaths = int.parse(infantDeathsController.text);
      double bmi = double.parse(bmiController.text);
      double gdp = double.parse(gdpController.text);
      double schooling = double.parse(schoolingController.text);

      // Check ranges
      if (adultMortality < 1.0 || adultMortality > 1000.0) {
        throw Exception('Adult Mortality must be between 1.0 and 1000.0');
      }
      if (infantDeaths < 0 || infantDeaths > 1000) {
        throw Exception('Infant Deaths must be between 0 and 1000');
      }
      if (bmi < 1.0 || bmi > 60.0) {
        throw Exception('BMI must be between 1.0 and 60.0');
      }
      if (gdp < 10.0 || gdp > 150000.0) {
        throw Exception('GDP must be between 10.0 and 150000.0');
      }
      if (schooling < 0.0 || schooling > 25.0) {
        throw Exception('Schooling must be between 0.0 and 25.0');
      }
      return true;
    } catch (e) {
      setState(() {
        resultMessage = 'Error: ${e.toString()}';
        resultColor = Colors.red;
      });
      return false;
    }
  }

  // Make prediction API call
  Future<void> makePrediction() async {
    if (!validateInputs()) {
      return;
    }

    setState(() {
      isLoading = true;
      resultMessage = 'Loading...';
      resultColor = Colors.blue;
    });

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'adult_mortality': double.parse(adultMortalityController.text),
          'infant_deaths': int.parse(infantDeathsController.text),
          'bmi': double.parse(bmiController.text),
          'gdp': double.parse(gdpController.text),
          'schooling': double.parse(schoolingController.text),
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          resultMessage =
              'Predicted Life Expectancy: ${data['predicted_life_expectancy_years']} years';
          resultColor = Colors.green;
          isLoading = false;
        });
      } else {
        setState(() {
          resultMessage = 'Error: Failed to get prediction (${response.statusCode})';
          resultColor = Colors.red;
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        resultMessage = 'Error: Unable to connect to API - $e';
        resultColor = Colors.red;
        isLoading = false;
      });
    }
  }

  // Clear form
  void clearForm() {
    adultMortalityController.clear();
    infantDeathsController.clear();
    bmiController.clear();
    gdpController.clear();
    schoolingController.clear();
    setState(() {
      resultMessage = '';
      resultColor = Colors.grey;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('African Life Expectancy Predictor'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              // Title
              Text(
                'Predict Life Expectancy',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(
                'Enter health and socioeconomic indicators for African nations',
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),

              // Adult Mortality Input
              _buildInputField(
                label: 'Adult Mortality (per 1000)',
                hint: '1.0 - 1000.0',
                controller: adultMortalityController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              // Infant Deaths Input
              _buildInputField(
                label: 'Infant Deaths (per 1000)',
                hint: '0 - 1000',
                controller: infantDeathsController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              // BMI Input
              _buildInputField(
                label: 'BMI (Body Mass Index)',
                hint: '1.0 - 60.0',
                controller: bmiController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              // GDP Input
              _buildInputField(
                label: 'GDP per Capita (USD)',
                hint: '10.0 - 150000.0',
                controller: gdpController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              // Schooling Input
              _buildInputField(
                label: 'Schooling (Years)',
                hint: '0.0 - 25.0',
                controller: schoolingController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 24),

              // Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton(
                    onPressed: isLoading ? null : makePrediction,
                    child: isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Predict'),
                  ),
                  ElevatedButton(
                    onPressed: isLoading ? null : clearForm,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.grey[600],
                    ),
                    child: const Text('Clear'),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Result Display
              if (resultMessage.isNotEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: resultColor.withOpacity(0.1),
                    border: Border.all(color: resultColor, width: 2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    resultMessage,
                    style: TextStyle(
                      color: resultColor,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  // Helper method to build input field
  Widget _buildInputField({
    required String label,
    required String hint,
    required TextEditingController controller,
    required TextInputType keyboardType,
  }) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      ),
    );
  }
}
