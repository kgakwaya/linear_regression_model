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

class _LifeExpectancyPredictorPageState
    extends State<LifeExpectancyPredictorPage> {
  final String apiUrl =
      'https://linear-regression-model-0uwb.onrender.com/predict';

  // Selected Country Code (Default 0: Algeria)
  int selectedCountryCode = 0;

  // Text controllers
  final TextEditingController adultMortalityController = TextEditingController();
  final TextEditingController infantDeathsController = TextEditingController();
  final TextEditingController bmiController = TextEditingController();
  final TextEditingController gdpController = TextEditingController();
  final TextEditingController schoolingController = TextEditingController();

  // African Countries Map
  final Map<int, String> africanCountriesMap = {
    0: 'Algeria', 1: 'Angola', 2: 'Benin', 3: 'Botswana', 4: 'Burkina Faso',
    5: 'Burundi', 6: 'Cameroon', 7: 'Cape Verde', 8: 'Central African Republic',
    9: 'Chad', 10: 'Comoros', 11: 'Congo', 12: "Cote d'Ivoire",
    13: 'Democratic Republic of the Congo', 14: 'Djibouti', 15: 'Egypt',
    16: 'Equatorial Guinea', 17: 'Eritrea', 18: 'Ethiopia', 19: 'Gabon',
    20: 'Gambia', 21: 'Ghana', 22: 'Guinea', 23: 'Guinea-Bissau', 24: 'Kenya',
    25: 'Lesotho', 26: 'Liberia', 27: 'Libya', 28: 'Madagascar', 29: 'Malawi',
    30: 'Mali', 31: 'Mauritania', 32: 'Mauritius', 33: 'Morocco', 34: 'Mozambique',
    35: 'Namibia', 36: 'Niger', 37: 'Nigeria', 38: 'Rwanda', 39: 'Sao Tome and Principe',
    40: 'Senegal', 41: 'Seychelles', 42: 'Sierra Leone', 43: 'Somalia', 44: 'South Africa',
    45: 'South Sudan', 46: 'Sudan', 47: 'Swaziland', 48: 'Togo', 49: 'Tunisia',
    50: 'Uganda', 51: 'United Republic of Tanzania', 52: 'Zambia', 53: 'Zimbabwe'
  };

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

  Future<void> makePrediction() async {
    if (!validateInputs()) return;

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
          'country': africanCountriesMap[selectedCountryCode],
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
          resultMessage =
              'Error: Failed to get prediction (${response.statusCode})';
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

  void clearForm() {
    adultMortalityController.clear();
    infantDeathsController.clear();
    bmiController.clear();
    gdpController.clear();
    schoolingController.clear();
    setState(() {
      selectedCountryCode = 0;
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

              // Country Dropdown
              DropdownButtonFormField<int>(
                value: selectedCountryCode,
                decoration: InputDecoration(
                  labelText: 'African Country',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                items: africanCountriesMap.entries.map((entry) {
                  return DropdownMenuItem<int>(
                    value: entry.key,
                    child: Text(entry.value),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() => selectedCountryCode = val);
                  }
                },
              ),
              const SizedBox(height: 16),

              _buildInputField(
                label: 'Adult Mortality (per 1000)',
                hint: '1.0 - 1000.0',
                controller: adultMortalityController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              _buildInputField(
                label: 'Infant Deaths (per 1000)',
                hint: '0 - 1000',
                controller: infantDeathsController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              _buildInputField(
                label: 'BMI (Body Mass Index)',
                hint: '1.0 - 60.0',
                controller: bmiController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              _buildInputField(
                label: 'GDP per Capita (USD)',
                hint: '10.0 - 150000.0',
                controller: gdpController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),

              _buildInputField(
                label: 'Schooling (Years)',
                hint: '0.0 - 25.0',
                controller: schoolingController,
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 24),

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
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      ),
    );
  }
}