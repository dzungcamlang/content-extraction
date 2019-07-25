# from sympy import Point, Line

# import time

# time_start = time.time()

# p_1 = Point(0, 2, evaluate=False)
# p_2 = Point(2, 0, evaluate=False)
# p_3 = Point(0, 0, evaluate=False)

# line = Line(p_1, p_2, evaluate=False)
# print(float(line.distance(p_3)))

# print(time.time() - time_start)



from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import time
 
desired = DesiredCapabilities.CHROME
desired ['loggingPrefs'] = { 'browser':'ALL' }

driver = webdriver.PhantomJS(desired_capabilities=desired)
driver.set_window_size(1440, 1028)
driver.get('https://www.aldi.com.au/')

print "Page is ready!"
 
script_content = """
var img = document.querySelector('body');
style = window.getComputedStyle(img, false);
console.log(JSON.stringify(style));
return style.backgroundImage;
"""

driver.save_screenshot("abc.jpeg")
result = driver.execute_script(script_content)
logs = driver.get_log('browser')
print(result)
print(logs)
