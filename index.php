<?php
// index.php

// Include config file and check if user is logged in
require_once "config.php";

if(!isset($_SESSION["loggedin"]) || $_SESSION["loggedin"] !== true){
    header("location: login.php");
    exit;
}

$prediction_result = "";
$error_message = "";
$recommended_crops_data = []; // New array to hold parsed compatible crop data for display
$incompatible_crops_data = []; // New array to hold parsed incompatible crop data for display

// Initialize variables to prevent "Undefined array key" warnings on initial load
$nitrogen = '40';
$phosphorus = '20';
$potassium = '10';
$climate = '';
$humidity = '';
$ph = '7'; // Default pH to neutral
$rainfall = '';
$soil_type = '';
$topography = '';
$water_availability = '';

// Initialize $selected_npk_option to prevent "Undefined variable" warning on initial load
$selected_npk_option = 'balanced-40-20-10'; // Initialize with a default value

// Define a mapping of NPK option values to their actual N, P, K numbers
$npk_compositions = [
    'balanced-40-20-10' => ['N' => 40, 'P' => 20, 'K' => 10], // Our new default
    'balanced-10-10-10' => ['N' => 10, 'P' => 10, 'K' => 10],
    'high-n-20-5-5' => ['N' => 20, 'P' => 5, 'K' => 5],
    'high-p-10-20-10' => ['N' => 10, 'P' => 20, 'K' => 10],
    'high-k-5-10-20' => ['N' => 5, 'P' => 10, 'K' => 20],
    'starter-18-24-12' => ['N' => 18, 'P' => 24, 'K' => 12],
    'flowering-5-10-10' => ['N' => 5, 'P' => 10, 'K' => 10],
    'vegetative-growth-20-10-10' => ['N' => 20, 'P' => 10, 'K' => 10],
];

// Variables to store submitted conditions for display
$submitted_npk_label = '';
$submitted_climate = '';
$submitted_humidity = '';
$submitted_ph = '';
$submitted_rainfall = '';
$submitted_soil_type = '';
$submitted_topography = '';
$submitted_water_availability = '';

// Flag to check if the request is from admin_dashboard
$is_admin_view = (isset($_GET['admin_view']) && $_GET['admin_view'] === 'true' && isset($_SESSION["role"]) && $_SESSION["role"] === 'admin');

// Determine if we should process the prediction immediately (for admin view) or wait for POST
$should_process_prediction = false;

if ($is_admin_view) {
    // Populate variables from GET parameters for admin view
    $nitrogen = isset($_GET['nitrogen']) ? $_GET['nitrogen'] : '40';
    $phosphorus = isset($_GET['phosphorus']) ? $_GET['phosphorus'] : '20';
    $potassium = isset($_GET['potassium']) ? $_GET['potassium'] : '10';
    $climate = isset($_GET['climate']) ? $_GET['climate'] : '';
    $humidity = isset($_GET['humidity']) ? $_GET['humidity'] : '';
    $ph = isset($_GET['ph']) ? $_GET['ph'] : '7';
    $rainfall = isset($_GET['rainfall']) ? $_GET['rainfall'] : '';
    $soil_type = isset($_GET['soil_type']) ? $_GET['soil_type'] : '';
    $topography = isset($_GET['topography']) ? $_GET['topography'] : '';
    $water_availability = isset($_GET['water_availability']) ? $_GET['water_availability'] : '';
    $selected_npk_option = isset($_GET['npk_option']) ? $_GET['npk_option'] : 'balanced-40-20-10';

    // Set submitted labels for display
    $submitted_npk_label = htmlspecialchars(ucwords(str_replace('-', ' ', $selected_npk_option)));
    $submitted_climate = $climate;
    $submitted_humidity = $humidity;
    $submitted_ph = $ph;
    $submitted_rainfall = $rainfall;
    $submitted_soil_type = $soil_type;
    $submitted_topography = $topography;
    $submitted_water_availability = $water_availability;

    $should_process_prediction = true;

} elseif($_SERVER["REQUEST_METHOD"] == "POST"){
    // Processing form data when form is submitted by a regular user
    $selected_npk_option = trim($_POST['npk_option']);

    // Get NPK values based on the selected option
    if (array_key_exists($selected_npk_option, $npk_compositions)) {
        $nitrogen = $npk_compositions[$selected_npk_option]['N'];
        $phosphorus = $npk_compositions[$selected_npk_option]['P'];
        $potassium = $npk_compositions[$selected_npk_option]['K'];
        $submitted_npk_label = array_search($npk_compositions[$selected_npk_option], $npk_compositions); // Get the label
    } else {
        // Fallback to default 40:20:10 if selected option is invalid
        $nitrogen = '40';
        $phosphorus = '20';
        $potassium = '10';
        $error_message = "Invalid NPK composition selected. Using default (40:20:10).";
        $submitted_npk_label = 'balanced-40-20-10';
    }

    $climate = trim($_POST['climate']);
    $humidity = trim($_POST['humidity']);
    $ph = trim($_POST['ph']);
    $rainfall = trim($_POST['rainfall']);
    $soil_type = trim($_POST['soil_type']);
    $topography = trim($_POST['topography']);
    $water_availability = trim($_POST['water_availability']);

    // Store submitted values for display
    $submitted_climate = $climate;
    $submitted_humidity = $humidity;
    $submitted_ph = $ph;
    $submitted_rainfall = $rainfall;
    $submitted_soil_type = $soil_type;
    $submitted_topography = $topography;
    $submitted_water_availability = $water_availability;

    $should_process_prediction = true;
}

if ($should_process_prediction) {
    // --- Call Python Model ---
    // The data is passed as command line arguments to the python script.
    // Ensure the order and number of arguments matches your model.py's expected input.
    $command = escapeshellcmd("python model.py " .
               escapeshellarg($nitrogen) . " " . escapeshellarg($phosphorus) . " " . escapeshellarg($potassium) . " " . // Corrected typo here
               escapeshellarg($climate) . " " . escapeshellarg($humidity) . " " . escapeshellarg($ph) . " " . escapeshellarg($rainfall) . " " .
               escapeshellarg($soil_type) . " " . escapeshellarg($topography) . " " . escapeshellarg($water_availability));
    $output = shell_exec($command);

    if ($output !== null) {
        $prediction_result = trim($output);

        // Attempt to decode the JSON output from model.py
        $decoded_output = json_decode($prediction_result, true);

        if (json_last_error() === JSON_ERROR_NONE && isset($decoded_output['compatible_crops']) && isset($decoded_output['incompatible_crops'])) {
            $recommended_crops_data = $decoded_output['compatible_crops'];
            $incompatible_crops_data = $decoded_output['incompatible_crops'];

            // Set a general message for display, as specific crop names are now in arrays
            if (!empty($recommended_crops_data) || !empty($incompatible_crops_data)) {
                $prediction_result = "Crop recommendations generated successfully.";
            } else {
                $prediction_result = "No crop data received from the model.";
            }

        } else {
            // If JSON decoding fails, or expected keys are missing, treat as an error
            $error_message = "Error parsing model output: " . $prediction_result;
            $prediction_result = ""; // Clear prediction result if there's a parsing error
        }

        // --- Store Prediction in Database ---
        // Only store if it's not an admin viewing from the dashboard (to avoid duplicate entries for admin views)
        if (isset($_SESSION["id"]) && $_SESSION["id"] !== null && !$is_admin_view) {
            $user_id = $_SESSION["id"];
            // Updated SQL to include 'temperature' and its placeholder
            $sql = "INSERT INTO predictions (user_id, nitrogen, phosphorus, potassium, climate, temperature, humidity, ph, rainfall, soil_type, topography, water_availability, predicted_crop) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

            if($stmt = mysqli_prepare($link, $sql)){
                $dummy_temperature = 0.0; // Placeholder for temperature
                // Store the full JSON output in a variable before binding
                $json_encoded_output = json_encode($decoded_output);

                // Corrected type definition string: 'iiiisddddssss' (13 parameters)
                // i: user_id, nitrogen, phosphorus, potassium
                // s: climate
                // d: temperature, humidity, ph, rainfall
                // s: soil_type, topography, water_availability, predicted_crop
                mysqli_stmt_bind_param($stmt, "iiiisddddssss",
                    $user_id,
                    $nitrogen,
                    $phosphorus,
                    $potassium,
                    $climate,
                    $dummy_temperature,
                    $humidity,
                    $ph,
                    $rainfall,
                    $soil_type,
                    $topography,
                    $water_availability,
                    $json_encoded_output // Pass the variable here
                );

                if(!mysqli_stmt_execute($stmt)){
                    $error_message = "Error: Could not store the prediction. " . mysqli_error($link);
                }
                mysqli_stmt_close($stmt);
            } else {
                $error_message = "Error: Could not prepare SQL statement for prediction storage. " . mysqli_error($link);
            }
        } elseif ($is_admin_view) {
             // Do nothing - don't store prediction if it's an admin view from dashboard
        } else {
            $error_message = "Error: User not logged in. Cannot store prediction.";
        }
    } else {
        $error_message = "Error: Could not get a prediction from the model. Please check model.py and its dependencies. Output: " . htmlspecialchars($output);
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crop Recommendation System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        /* Custom styles for the range slider labels */
        .ph-labels {
            display: flex;
            justify-content: space-between;
            width: 100%;
            margin-top: 0.5rem;
            font-size: 0.875rem; /* text-sm */
            color: #6B7280; /* text-gray-500 */
        }
        .ph-labels span {
            position: relative;
            transform: translateX(-50%);
            left: 50%;
        }
        .ph-labels .label-acid { left: 0; transform: translateX(0); }
        .ph-labels .label-neutral { left: 50%; transform: translateX(-50%); }
        .ph-labels .label-basic { left: 100%; transform: translateX(-100%); }

        /* Custom CSS for smoother collapse (Bootstrap's default transition) */
        /* These ensure Bootstrap's collapse transitions are respected */
        .collapsing {
            height: 0;
            overflow: hidden;
            transition: height .35s ease; /* Bootstrap's default transition */
        }
        /* No .collapse:not(.show) or .collapse.show here, visibility is controlled by JS */
    </style>
</head>
<body class="bg-gradient-to-br from-gray-900 to-gray-800 text-gray-100 min-h-screen flex items-center justify-center py-10">
    <div class="container mx-auto p-6 bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-green-400 mb-2">Hi, <span class="text-white"><?php echo htmlspecialchars($_SESSION["username"]); ?></span>!</h1>
            <p class="text-lg text-gray-300">Welcome to the Crop Recommendation System.</p>
            <?php if ($is_admin_view): ?>
                <a href="admin/admin_dashboard.php" class="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105">
                    Back to Admin Dashboard
                </a>
            <?php else: ?>
                <a href="logout.php" class="mt-4 inline-block bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105">
                    Sign Out of Your Account
                </a>
            <?php endif; ?>
        </div>

        <h2 class="text-3xl font-semibold text-center text-white mb-6">Crop Recommendation Form</h2>
        <p class="text-gray-300 text-center mb-8">Enter the soil and weather conditions to get a crop recommendation.</p>

        <div id="recommendationFormContainer" class="<?php echo ($should_process_prediction && !empty($prediction_result) && (!empty($recommended_crops_data) || !empty($incompatible_crops_data))) || (!empty($error_message)) ? 'hidden' : ''; ?>">
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post" class="space-y-6">
                <div class="bg-gray-700 p-6 rounded-lg shadow-inner">
                    <label for="npk_option" class="block text-sm font-medium text-gray-300 mb-2">
                        Select Mineral (NPK Composition)
                    </label>
                    <select
                        id="npk_option"
                        name="npk_option"
                        class="block w-full px-4 py-3 bg-gray-900 border border-gray-600 rounded-md shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-150 ease-in-out"
                        required
                    >
                        <?php foreach($npk_compositions as $value => $composition): ?>
                            <option value="<?php echo htmlspecialchars($value); ?>" <?php echo ($selected_npk_option == $value) ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars(ucwords(str_replace('-', ' ', $value))) . " (N:{$composition['N']}, P:{$composition['P']}, K:{$composition['K']})"; ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="climate" class="block text-sm font-medium text-gray-300 mb-1">Climate</label>
                        <select id="climate" name="climate" class="w-full p-3 bg-gray-900 border border-gray-600 rounded-md focus:ring-green-500 focus:border-green-500 text-white transition duration-200" required>
                            <option value="">Select Climate Type</option>
                            <option value="Tropical" <?php echo ($climate == 'Tropical') ? 'selected' : ''; ?>>Tropical</option>
                            <option value="Temperate" <?php echo ($climate == 'Temperate') ? 'selected' : ''; ?>>Temperate</option>
                            <option value="Arid" <?php echo ($climate == 'Arid') ? 'selected' : ''; ?>>Arid</option>
                            </select>
                    </div>
                    <div>
                        <label for="humidity" class="block text-sm font-medium text-gray-300 mb-1">Humidity (%)</label>
                        <input type="number" name="humidity" id="humidity" class="w-full p-3 bg-gray-900 border border-gray-600 rounded-md focus:ring-green-500 focus:border-green-500 text-white placeholder-gray-400 transition duration-200" required value="<?php echo htmlspecialchars($humidity); ?>" min="0" max="100">
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="phRange" class="block text-sm font-medium text-gray-300 mb-1">pH Level</label>
                        <input type="range" class="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer range-lg focus:outline-none focus:ring-2 focus:ring-green-500 accent-green-500" id="phRange" name="ph" min="0" max="14" step="0.1" value="<?php echo htmlspecialchars($ph); ?>" oninput="this.nextElementSibling.nextElementSibling.value = this.value" required>
                        <div class="ph-labels">
                            <span class="label-acid">0-6: Acid</span>
                            <span class="label-neutral">7: Neutral</span>
                            <span class="label-basic">8-14: Basic</span>
                        </div>
                        <output class="block text-center text-sm text-gray-300 mt-2"><?php echo htmlspecialchars($ph); ?></output>
                    </div>
                    <div>
                        <label for="rainfall" class="block text-sm font-medium text-gray-300 mb-1">Rainfall (mm)</label>
                        <input type="number" name="rainfall" id="rainfall" class="w-full p-3 bg-gray-900 border border-gray-600 rounded-md focus:ring-green-500 focus:border-green-500 text-white placeholder-gray-400 transition duration-200" required value="<?php echo htmlspecialchars($rainfall); ?>" min="0">
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="soil_type" class="block text-sm font-medium text-gray-300 mb-1">Soil Type</label>
                        <select id="soil_type" name="soil_type" class="w-full p-3 bg-gray-900 border border-gray-600 rounded-md focus:ring-green-500 focus:border-green-500 text-white transition duration-200" required>
                            <option value="">Select Soil Type</option>
                            <option value="Loamy" <?php echo ($soil_type == 'Loamy') ? 'selected' : ''; ?>>Loamy</option>
                            <option value="Sandy" <?php echo ($soil_type == 'Sandy') ? 'selected' : ''; ?>>Sandy</option>
                            <option value="Clayey" <?php echo ($soil_type == 'Clayey') ? 'selected' : ''; ?>>Clayey</option>
                            <option value="Silty" <?php echo ($soil_type == 'Silty') ? 'selected' : ''; ?>>Silty</option>
                            <option value="Peaty" <?php echo ($soil_type == 'Peaty') ? 'selected' : ''; ?>>Peaty</option>
                            </select>
                    </div>
                    <div>
                        <label for="topography" class="block text-sm font-medium text-gray-300 mb-1">Topography</label>
                        <select id="topography" name="topography" class="w-full p-3 bg-gray-900 border border-gray-600 rounded-md focus:ring-green-500 focus:border-green-500 text-white transition duration-200" required>
                            <option value="">Select Topography</option>
                            <option value="Flat" <?php echo ($topography == 'Flat') ? 'selected' : ''; ?>>Flat</option>
                            <option value="Sloped" <?php echo ($topography == 'Sloped') ? 'selected' : ''; ?>>Sloped</option>
                            <option value="Hilly" <?php echo ($topography == 'Hilly') ? 'selected' : ''; ?>>Hilly</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label for="water_availability" class="block text-sm font-medium text-gray-300 mb-1">Water Availability</label>
                    <select id="water_availability" name="water_availability" class="w-full p-3 bg-gray-900 border border-gray-600 rounded-md focus:ring-green-500 focus:border-green-500 text-white transition duration-200" required>
                        <option value="">Select Water Availability</option>
                        <option value="High" <?php echo ($water_availability == 'High') ? 'selected' : ''; ?>>High</option>
                        <option value="Medium" <?php echo ($water_availability == 'Medium') ? 'selected' : ''; ?>>Medium</option>
                        <option value="Low" <?php echo ($water_availability == 'Low') ? 'selected' : ''; ?>>Low</option>
                    </select>
                </div>

                <div class="text-center pt-4">
                    <input type="submit" class="w-full md:w-auto bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105 cursor-pointer" value="Get Recommendation">
                </div>
            </form>
        </div> <!-- End of recommendationFormContainer -->

        <!-- Prediction Result Display - Always present, visibility controlled by JS -->
        <div class="mt-8 p-6 bg-green-800 rounded-lg shadow-xl text-center <?php echo (!empty($prediction_result) && (!empty($recommended_crops_data) || !empty($incompatible_crops_data))) ? '' : 'hidden'; ?>" id="predictionResultDisplay">
            <h3 class="text-2xl font-bold text-green-200 mb-4">Conditions Used for Recommendation:</h3>
            <div class="bg-gray-700 p-4 rounded-lg shadow-md text-left mb-6 grid grid-cols-1 md:grid-cols-2 gap-2 text-gray-300">
                <div><strong>NPK Composition:</strong> <?php echo htmlspecialchars(ucwords(str_replace('-', ' ', $selected_npk_option))); ?> (N:<?php echo htmlspecialchars($nitrogen); ?>, P:<?php echo htmlspecialchars($phosphorus); ?>, K:<?php echo htmlspecialchars($potassium); ?>)</div>
                <div><strong>Climate:</strong> <?php echo htmlspecialchars($submitted_climate); ?></div>
                <div><strong>Humidity:</strong> <?php echo htmlspecialchars($submitted_humidity); ?>%</div>
                <div><strong>pH Level:</strong> <?php echo htmlspecialchars($submitted_ph); ?></div>
                <div><strong>Rainfall:</strong> <?php echo htmlspecialchars($submitted_rainfall); ?> mm</div>
                <div><strong>Soil Type:</strong> <?php echo htmlspecialchars($submitted_soil_type); ?></div>
                <div><strong>Topography:</strong> <?php echo htmlspecialchars($submitted_topography); ?></div>
                <div><strong>Water Availability:</strong> <?php echo htmlspecialchars($submitted_water_availability); ?></div>
            </div>

            <h4 class="text-2xl font-bold text-green-200 mb-4">Recommended Crops:</h4>

            <?php if (!empty($recommended_crops_data)): ?>
                <div class="space-y-4 mb-6">
                    <?php foreach ($recommended_crops_data as $crop_item): ?>
                        <div class="bg-gray-700 p-4 rounded-lg shadow-md">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-lg font-semibold text-white"><?php echo htmlspecialchars($crop_item['crop']); ?></span>
                                <span class="text-green-300 font-bold"><?php echo number_format($crop_item['compatibility'], 2); ?>%</span>
                            </div>
                            <div class="w-full bg-gray-600 rounded-full h-2.5">
                                <div class="bg-green-500 h-2.5 rounded-full" style="width: <?php echo htmlspecialchars($crop_item['compatibility']); ?>%;"></div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php else: ?>
                <p class="text-gray-300 mb-4">No crops found with compatibility above 0% for the given conditions.</p>
            <?php endif; ?>

            <?php if (!empty($incompatible_crops_data)): ?>
                <div class="mt-6">
                    <!-- Title for Incompatible Crops section -->
                    <h4 class="text-2xl font-bold text-red-300 mb-4">Incompatible Crops (<?php echo count($incompatible_crops_data); ?>):</h4>
                    <div class="space-y-3 p-4 bg-gray-700 rounded-lg shadow-inner max-h-60 overflow-y-auto">
                        <?php foreach ($incompatible_crops_data as $crop_item): ?>
                            <div class="flex justify-between items-center text-gray-300 text-sm">
                                <span><?php echo htmlspecialchars($crop_item['crop']); ?></span>
                                <span><?php echo number_format($crop_item['compatibility'], 2); ?>%</span>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>

            <!-- Added separate reset button -->
            <div class="text-center mt-6">
                <button class="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-300 ease-in-out"
                        onclick="resetForm()">
                    Make Another Recommendation
                </button>
            </div>
        </div>

        <!-- Error Message Display - Always present, visibility controlled by JS -->
        <div class="mt-8 p-6 bg-red-800 rounded-lg shadow-xl text-center <?php echo !empty($error_message) ? '' : 'hidden'; ?>" id="errorMessageDisplay">
            <p class="text-red-200 font-medium"><?php echo htmlspecialchars($error_message); ?></p>
            <button class="w-full md:w-auto mt-6 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105" onclick="resetForm()">Try Again</button>
        </div>
    </div>
    <!-- jQuery and Bootstrap JS for collapse functionality -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // JavaScript to handle form visibility and reset
        $(document).ready(function() {
            // Get references to the form container and result/error display divs
            const formContainer = $('#recommendationFormContainer');
            const predictionResultDisplay = $('#predictionResultDisplay');
            const errorMessageDisplay = $('#errorMessageDisplay');

            // PHP variables passed to JavaScript to control initial display
            const shouldProcessPrediction = <?php echo json_encode($should_process_prediction); ?>;
            const hasPredictionResult = <?php echo json_encode(!empty($prediction_result) && (!empty($recommended_crops_data) || !empty($incompatible_crops_data))); ?>;
            const hasErrorMessage = <?php echo json_encode(!empty($error_message)); ?>;

            // Initial visibility based on PHP state
            if (shouldProcessPrediction && hasPredictionResult) {
                formContainer.addClass('hidden'); // Hide the form
                predictionResultDisplay.removeClass('hidden'); // Show the prediction result
                errorMessageDisplay.addClass('hidden'); // Ensure error is hidden
            } else if (hasErrorMessage) {
                formContainer.addClass('hidden'); // Hide the form even if there's an error
                predictionResultDisplay.addClass('hidden'); // Ensure prediction is hidden
                errorMessageDisplay.removeClass('hidden'); // Show the error message
            } else {
                formContainer.removeClass('hidden'); // Show the form on initial load
                predictionResultDisplay.addClass('hidden'); // Ensure prediction is hidden
                errorMessageDisplay.addClass('hidden'); // Ensure error is hidden
            }

            // Function to reset the form and show it again
            window.resetForm = function() { // Make it global for onclick
                // Clear URL parameters
                const currentUrl = new URL(window.location.href);
                currentUrl.search = ''; // Remove all query parameters
                window.history.pushState({}, '', currentUrl); // Update URL without reloading

                formContainer.removeClass('hidden'); // Show the form
                predictionResultDisplay.addClass('hidden'); // Hide the prediction result
                errorMessageDisplay.addClass('hidden'); // Hide the error message

                // Reset form fields to their default state (optional, if you want a clean form)
                $('form')[0].reset();
                $('#phRange').next().next().text($('#phRange').val()); // Update pH output
                // For select elements, you might need to manually set the selected option if not done by reset()
                $('#npk_option').val('balanced-40-20-10'); // Set default NPK option
            };

            // Initialize pH output display on page load
            document.addEventListener('DOMContentLoaded', (event) => {
                const phRange = document.getElementById('phRange');
                const phOutput = phRange.nextElementSibling.nextElementSibling;
                phOutput.value = phRange.value;
            });
        });
    </script>
</body>
</html>
