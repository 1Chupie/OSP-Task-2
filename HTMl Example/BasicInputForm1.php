<!DOCTYPE html>
<html>
<head>
    <title>Basic Input Form</title>
</head>
<body>

    <h2> Basic Input Form</h2>


    <form action="/action_page.php">
    <fieldset>
    <legend>Enter Your Name:</legend>
    <label for="fname">First name:</label><br>
    <input type="text" id="fname" name="fname" value="James"><br>
    <label for="lname">Last name:</label><br>
    <input type="text" id="lname" name="lname" value="Doakes"><br></br>
    <label for="email">Email Address:</label><br>
    <input type="email" id="email" name="email" value="djames@dexter.com"><br></br>
    <input type="submit" value="Submit">
    </fieldset>
</form>
</body>
</html>