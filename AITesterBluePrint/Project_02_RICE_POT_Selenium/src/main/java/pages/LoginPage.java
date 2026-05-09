package pages;

import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class LoginPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    @FindBy(xpath = "//input[@type='email']")
    private WebElement username;

    @FindBy(xpath = "//input[@type='password']")
    private WebElement password;

    @FindBy(xpath = "//input[@name='Login']")
    private WebElement loginButton;

    @FindBy(xpath = "//div[@id='error']")
    private WebElement errorMessage;

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        PageFactory.initElements(driver, this);
    }

    public void enterUsername(String user) throws Exception {
        try {
            wait.until(ExpectedConditions.visibilityOf(username)).sendKeys(user);
        } catch (TimeoutException e) {
            throw new Exception(e.getMessage());
        }
    }

    public void enterPassword(String pass) throws Exception {
        try {
            wait.until(ExpectedConditions.visibilityOf(password)).sendKeys(pass);
        } catch (TimeoutException e) {
            throw new Exception(e.getMessage());
        }
    }

    public void clickLogin() throws Exception {
        try {
            wait.until(ExpectedConditions.elementToBeClickable(loginButton)).click();
        } catch (TimeoutException e) {
            throw new Exception(e.getMessage());
        }
    }

    public String getErrorMessage() throws Exception {
        try {
            return wait.until(ExpectedConditions.visibilityOf(errorMessage)).getText();
        } catch (TimeoutException e) {
            throw new Exception(e.getMessage());
        }
    }

    public void doLogin(String user, String pass) throws Exception {
        enterUsername(user);
        enterPassword(pass);
        clickLogin();
    }
}
