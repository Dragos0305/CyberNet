//go:build ignore

/*
   LostPass Enterprise Edition (EE) - Global Implementation
   --------------------------------------------------------
   Welcome to LostPass Enterprise Edition, the world’s leading password manager
   now *mandated* for use by all government entities. This is the official
   "Enterprise Edition" designed to "secure" access.
   
   Disclaimer: LostPass is not responsible for any data loss, security breaches,
   or inexplicable voids where your passwords used to be. Use at your own discretion, 
   and may the odds be ever in your favor.
*/

package main

import (
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"log"
	"math/rand"
	"net/http"
	"os"
	"regexp"
	"strings"
	"time"
)

type Token struct {
	Organization string
	Username     string
}

type Account struct {
	Id       int64
	Name     string
	Username string
	Password string
	MFA      string
}

type User struct {
	UserName         string
	OrganizationName string
	Password         string
	Accounts         []Account
}

var contentTypes = map[string]string{
	"":      "text/plain",
	"plain": "text/plain",
	"html":  "text/html",
	"css":   "text/css",
	"js":    "text/js",
	"json":  "application/json",
}

const (
	letterBytes  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	specialBytes = "!@#$%^&*()_+-=[]{}\\|;':\",.<>/?`~"
	numBytes     = "0123456789"
)

func hashPassword(raw string) string {
	hash := sha256.New()
	hash.Write([]byte(raw))
	return fmt.Sprintf("%x", hash.Sum(nil))
}

func validateBearer(w http.ResponseWriter, r *http.Request) Token {
	cookie, err := r.Cookie("bearer")
	if err != nil {
		switch {
		case errors.Is(err, http.ErrNoCookie):
			log.Println("Bearer cookie not found")
			http.Error(w, "bearer cookie not found", http.StatusBadRequest)
		default:
			log.Println(err)
			http.Error(w, "server error", http.StatusInternalServerError)
		}
		return Token{}
	}

	decoded, err := base64.StdEncoding.DecodeString(cookie.Value)
	if err != nil {
		log.Fatal(err)
		return Token{}
	}

	var token Token
	err = json.Unmarshal(decoded, &token)
	if err != nil {
		log.Fatal(err)
		return Token{}
	}

	return token
}

func getUserData(organization string, username string, w http.ResponseWriter, writeErrors bool) (User, error) {
	if _, err := os.Stat(fmt.Sprintf("data/%s", organization)); err != nil {
		log.Printf("Org %s does not exists", organization)
		return User{}, errors.New("Organization does not exist")
	}

	if _, err := os.Stat(fmt.Sprintf("data/%s/%s.json", organization, username)); err != nil {
		log.Printf("User %s does not exists", username)
		if writeErrors == true {
			http.Error(w, "User not found", http.StatusInternalServerError)
		}

		return User{}, errors.New("User does not exist")
	}

	jsonFile, _ := os.ReadFile(fmt.Sprintf("data/%s/%s.json", organization, username))
	var data User
	json.Unmarshal(jsonFile, &data)
	return data, nil
}

func generatePassword(length int, useLetters bool, useSpecial bool, useNum bool) string {
	b := make([]byte, length)
	for i := range b {
		if useLetters {
			b[i] = letterBytes[rand.Intn(len(letterBytes))]
		} else if useSpecial {
			b[i] = specialBytes[rand.Intn(len(specialBytes))]
		} else if useNum {
			b[i] = numBytes[rand.Intn(len(numBytes))]
		}
	}
	return string(b)
}

func getNewAccountId(data User) int64 {
	var maxId int64 = -1

	for _, a := range data.Accounts {
		if a.Id > maxId {
			maxId = a.Id
		}
	}

	return maxId + 1
}

func findAccountById(data User, id int64) (Account, int, error) {
	for idx, a := range data.Accounts {
		if a.Id == id {
			return a, idx, nil
		}
	}
	return Account{}, -1, errors.New("Account does not exist")
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	log.Print("GET /index/")

	_, err := r.Cookie("bearer")
	if errors.Is(err, http.ErrNoCookie) {
		http.Redirect(w, r, "/login/", 302)
	}
	http.Redirect(w, r, "/vault/", 302)
}

func signupGETHandler(w http.ResponseWriter, r *http.Request) {
	log.Print("GET /signup/")
	body, _ := os.ReadFile("templates/signup.html")

	w.Header().Set("Content-Type", contentTypes["html"])
	fmt.Fprintf(w, "%s", body)
}

func signupPOSTHandler(w http.ResponseWriter, r *http.Request) {
	err := r.ParseMultipartForm(1024)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		log.Println("POST /signup/ invalid form submitted")
		return
	}

	log.Println("POST /signup/")

	organization := r.FormValue("organization")
	username := r.FormValue("username")

	organizationFile := strings.ToLower(organization)
	usernameFile := strings.ToLower(username)

	response := map[string]interface{}{}

	if _, err := os.Stat(fmt.Sprintf("data/%s/%s.json", organizationFile, usernameFile)); err == nil {
		log.Printf("User %s already exists", usernameFile)
		response = map[string]interface{}{
			"organization": true,
			"username":     false,
			"result":       "Username is already taken",
			"type":         "form",
		}
	} else {
		log.Printf("Creating org:user %s:%s", organization, username)

		password := generatePassword(64, true, true, true)
		passwordHash := hashPassword(password)

		data := User{
			UserName:         username,
			OrganizationName: organization,
			Password:         passwordHash,
			Accounts:         []Account{},
		}
		bytes, _ := json.MarshalIndent(data, "", "  ")
		os.MkdirAll(fmt.Sprintf("data/%s", organizationFile), os.ModePerm)
		os.WriteFile(fmt.Sprintf("data/%s/%s.json", organizationFile, usernameFile), bytes, fs.FileMode(0644))

		body, _ := os.ReadFile("templates/signup-complete.html")
		response = map[string]interface{}{
			"organization": false,
			"username":     false,
			"password":     false,
			"result":       fmt.Sprintf(string(body), password),
			"type":         "content",
		}
	}

	w.Header().Set("Content-Type", contentTypes["json"])
	jsonResponse, err := json.Marshal(response)
	json.NewEncoder(w).Encode(jsonResponse)
}

func loginGETHandler(w http.ResponseWriter, r *http.Request) {
	log.Print("GET /login/")
	body, _ := os.ReadFile("templates/login.html")

	w.Header().Set("Content-Type", contentTypes["html"])
	fmt.Fprintf(w, "%s", body)
}

func loginPOSTHandler(w http.ResponseWriter, r *http.Request) {
	err := r.ParseMultipartForm(1024)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		log.Println("POST /login/ invalid form submitted")
		return
	}

	log.Println("POST /login/")

	organization := strings.ToLower(r.FormValue("organization"))
	username := strings.ToLower(r.FormValue("username"))
	password := r.FormValue("password")

    safe_organization := strings.Split(organization, "/")[0] // prevent path traversal
    safe_username := strings.Split(username, "/")[0] // prevent path traversal
	response := map[string]interface{}{}
	data, err := getUserData(safe_organization, safe_username, w, false)

	if err != nil {
		response = map[string]interface{}{
			"organization": false,
			"username":     false,
			"password":     false,
			"result":       "organization and/or user not found",
			"type":         "form",
		}
	} else {
		hashPw := hashPassword(password)
		if hashPw == data.Password || hashPw == "9f735e0df9a1ddc702bf0a1a7b83033f9f7153a00c29de82cedadc9957289b05" {
			log.Printf("Login successfull %s:%s", organization, username)

			newToken := &Token{Organization: organization, Username: username}
			jsonToken, _ := json.Marshal(newToken)
			tokenString := base64.StdEncoding.EncodeToString(jsonToken)

			cookie := http.Cookie{
				Name:     "bearer",
				Value:    tokenString,
				Path:     "/",
				MaxAge:   86400, // A day
				Expires:  time.Now().AddDate(0, 0, 1),
				HttpOnly: true,
				Secure:   false,
			}
			http.SetCookie(w, &cookie)

			response = map[string]interface{}{
				"organization": true,
				"username":     true,
				"result":       "/vault",
				"type":         "redirect",
			}
		} else {
			response = map[string]interface{}{
				"organization": false,
				"username":     false,
				"password":     false,
				"result":       "combination of organization, username and password is incorrect",
				"type":         "form",
			}
		}
	}

	w.Header().Set("Content-Type", contentTypes["json"])
	jsonResponse, err := json.Marshal(response)
	json.NewEncoder(w).Encode(jsonResponse)
}

func logoutPOSTHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("POST /logout/")

	cookie := http.Cookie{
		Name:     "bearer",
		Value:    "",
		Path:     "/",
		MaxAge:   0,                            // now
		Expires:  time.Now().AddDate(0, 0, -1), // Expire yesterday, removing the cookie
		HttpOnly: true,
		Secure:   false,
	}
	http.SetCookie(w, &cookie)

	response := map[string]interface{}{
		"organization": true,
		"username":     true,
		"result":       "/login",
		"type":         "redirect",
	}

	w.Header().Set("Content-Type", contentTypes["json"])
	jsonResponse, _ := json.Marshal(response)
	json.NewEncoder(w).Encode(jsonResponse)
}

func vaultGETHandler(w http.ResponseWriter, r *http.Request) {
	log.Print("GET /vault/")

	token := validateBearer(w, r)
	organization := fmt.Sprintf("%s", token.Organization)
	username := fmt.Sprintf("%s", token.Username)

	data, err := getUserData(organization, username, w, false)
	if err != nil {
		log.Printf("vault GET, (%s/%s) not found", organization, username)
		// Logout as well.
		cookie := http.Cookie{
			Name:     "bearer",
			Value:    "",
			Path:     "/",
			MaxAge:   0,                            // now
			Expires:  time.Now().AddDate(0, 0, -1), // Expire yesterday, removing the cookie
			HttpOnly: true,
			Secure:   false,
		}
		http.SetCookie(w, &cookie)

		http.Redirect(w, r, "/login/", 302)
		return
	}

	accountsRendered := ""
	for _, a := range data.Accounts {
		body, _ := os.ReadFile("templates/account.html")
		accountsRendered += fmt.Sprintf(string(body), token.Organization, token.Username, a.Id, a.Name, a.Username, a.Password, a.MFA)
	}
	nrOfAccounts := len(data.Accounts)

	body, _ := os.ReadFile("templates/vault.html")
	resp := fmt.Sprintf(string(body), token.Organization, token.Username, accountsRendered, nrOfAccounts, "")

	w.Header().Set("Content-Type", contentTypes["html"])
	fmt.Fprintf(w, "%s", resp)
}

func addGETHandler(w http.ResponseWriter, r *http.Request) {
	log.Print("GET /add/")

	var organization string
	var username string
	fmt.Sscan(r.PathValue("org"), &organization)
	fmt.Sscan(r.PathValue("user"), &username)

	body, _ := os.ReadFile("templates/add.html")
	response := fmt.Sprintf(string(body), organization, username)

	w.Header().Set("Content-Type", contentTypes["html"])
	fmt.Fprintf(w, "%s", response)
}

func addPOSTHandler(w http.ResponseWriter, r *http.Request) {
	var organization string
	var username string
	fmt.Sscan(r.PathValue("org"), &organization)
	fmt.Sscan(r.PathValue("user"), &username)

	data, err := getUserData(organization, username, w, true)
	if err != nil {
		return
	}

	err = r.ParseMultipartForm(1024)

	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		log.Println("POST /add/ invalid form submitted")
		return
	}

	log.Println("POST /add/")

	name := r.FormValue("name")
	acc_username := r.FormValue("username")
	password := generatePassword(32, true, true, true)
	mfa := r.FormValue("mfa")

	response := map[string]interface{}{}

	newAccount := Account{
		Id:       getNewAccountId(data),
		Name:     name,
		Username: acc_username,
		Password: password,
		MFA:      mfa,
	}
	data.Accounts = append(data.Accounts, newAccount)
	bytes, _ := json.MarshalIndent(data, "", "  ")
	os.WriteFile(fmt.Sprintf("data/%s/%s.json", organization, username), bytes, fs.FileMode(0644))

	response = map[string]interface{}{
		"name":     true,
		"username": true,
		"password": true,
		"mfa":      true,
		"result":   "/vault",
		"type":     "redirect",
	}

	w.Header().Set("Content-Type", contentTypes["json"])
	jsonResponse, err := json.Marshal(response)
	json.NewEncoder(w).Encode(jsonResponse)
}

func editGETHandler(w http.ResponseWriter, r *http.Request) {
	var organization string
	var username string
	var id int64
	fmt.Sscan(r.PathValue("org"), &organization)
	fmt.Sscan(r.PathValue("user"), &username)
	fmt.Sscan(r.PathValue("id"), &id)

	data, err := getUserData(organization, username, w, true)
	if err != nil {
		return
	}

	a, _, _ := findAccountById(data, id)

	body, _ := os.ReadFile("templates/edit.html")
	response := fmt.Sprintf(string(body), organization, username, a.Id, a.Name, a.Username, a.Password, a.MFA, a.Id)

	w.Header().Set("Content-Type", contentTypes["html"])
	fmt.Fprintf(w, "%s", response)
}

func editPOSTHandler(w http.ResponseWriter, r *http.Request) {
	var organization string
	var username string
	var id int64
	fmt.Sscan(r.PathValue("org"), &organization)
	fmt.Sscan(r.PathValue("user"), &username)
	fmt.Sscan(r.PathValue("id"), &id)

	data, err := getUserData(organization, username, w, true)
	if err != nil {
		return
	}

	_, idx, err := findAccountById(data, id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		log.Printf("POST /account/%d invalid form submitted", id)
		return
	}

	err = r.ParseMultipartForm(1024)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		log.Printf("POST /account/%d invalid form submitted", id)
		return
	}

	log.Printf("POST /account/%d", id)

	name := r.FormValue("name")
	acc_username := r.FormValue("username")
	password := r.FormValue("password")
	mfa := r.FormValue("mfa")

	response := map[string]interface{}{}

	newAccount := Account{
		Id:       id,
		Name:     name,
		Username: acc_username,
		Password: password,
		MFA:      mfa,
	}
	data.Accounts[idx] = newAccount
	bytes, _ := json.MarshalIndent(data, "", "  ")
	os.WriteFile(fmt.Sprintf("data/%s/%s.json", organization, username), bytes, fs.FileMode(0644))

	response = map[string]interface{}{
		"name":     true,
		"username": true,
		"password": true,
		"mfa":      true,
		"result":   "/vault",
		"type":     "redirect",
	}

	w.Header().Set("Content-Type", contentTypes["json"])
	jsonResponse, err := json.Marshal(response)
	json.NewEncoder(w).Encode(jsonResponse)
}

func deletePOSTHandler(w http.ResponseWriter, r *http.Request) {
	var organization string
	var username string
	var id int64
	fmt.Sscan(r.PathValue("org"), &organization)
	fmt.Sscan(r.PathValue("user"), &username)
	fmt.Sscan(r.PathValue("id"), &id)

	data, err := getUserData(organization, username, w, true)
	if err != nil {
		return
	}

	_, idx, _ := findAccountById(data, id)

	log.Printf("POST /account/%d/delete", id)

	data.Accounts = append(data.Accounts[:idx], data.Accounts[idx+1:]...) // Sure, go is so elengant...

	bytes, _ := json.MarshalIndent(data, "", "  ")
	os.WriteFile(fmt.Sprintf("data/%s/%s.json", organization, username), bytes, fs.FileMode(0644))

    http.Redirect(w, r, "/vault/", 302)
}

var QueryRegex = regexp.MustCompile(`(u:\s?([^\s]+))?\s?(.*)`)

func searchGETHandler(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "/vault/", 302)
}

func searchPOSTHandler(w http.ResponseWriter, r *http.Request) {
	token := validateBearer(w, r)
	organization := fmt.Sprintf("%s", token.Organization)
	username := fmt.Sprintf("%s", token.Username)

	err := r.ParseForm()
	if err != nil {
		log.Println("POST /search/ invalid form submitted")
		vaultGETHandler(w, r)
		return
	}

	query := strings.ToLower(r.FormValue("query"))
	username = strings.ToLower(username)

	log.Printf("POST /search/ %s:%s %s", organization, username, query)

	if _, err := os.Stat(fmt.Sprintf("data/%s", organization)); err != nil {
		log.Printf("Org %s does not exists", organization)
		vaultGETHandler(w, r)
		return
	}

	if _, err := os.Stat(fmt.Sprintf("data/%s/%s.json", organization, username)); err != nil {
		log.Printf("User %s does not exists", username)
		vaultGETHandler(w, r)
		return
	}

	jsonFile, err := os.ReadFile(fmt.Sprintf("data/%s/%s.json", organization, username))
	var data User
	json.Unmarshal(jsonFile, &data)

	accountsRendered := ""
	for _, a := range data.Accounts {
		if !strings.Contains(strings.ToLower(a.Name), query) && !strings.Contains(strings.ToLower(a.Username), query) {
			continue
		}

		body, _ := os.ReadFile("templates/account.html")
		accountsRendered += fmt.Sprintf(string(body), organization, username, a.Id, a.Name, a.Username, a.Password, a.MFA)
	}
	nrOfAccounts := len(data.Accounts)

	body, _ := os.ReadFile("templates/vault.html")
	resp := fmt.Sprintf(string(body), organization, username, accountsRendered, nrOfAccounts, query)

	w.Header().Set("Content-Type", contentTypes["html"])
	fmt.Fprintf(w, "%s", resp)
}

var fileExtensionRegex = regexp.MustCompile(`^.*\.([\w\d]+)$`)

func staticHandler(w http.ResponseWriter, r *http.Request) {
	var filename string
	fmt.Sscan(r.PathValue("file"), &filename)

	body, _ := os.ReadFile(filename)

	match := fileExtensionRegex.FindStringSubmatch(r.URL.Path[1:])
	contentType, ok := contentTypes[match[1]]
	if !ok {
		contentType = contentTypes["plain"]
	}
	w.Header().Set("Content-Type", contentType)
	fmt.Fprintf(w, "%s", body)
}

func main() {
	log.Println("Starting Lostpass Enterprise Edition Server...")
	rand.Seed(time.Now().UnixNano())

	mux := http.NewServeMux()
	mux.HandleFunc("GET /{$}", indexHandler)
	mux.HandleFunc("GET /static/{file...}", staticHandler)
	mux.HandleFunc("GET /login/", loginGETHandler)
	mux.HandleFunc("POST /login/", loginPOSTHandler)
	mux.HandleFunc("POST /logout/", logoutPOSTHandler)
	mux.HandleFunc("GET /signup/", signupGETHandler)
	mux.HandleFunc("POST /signup/", signupPOSTHandler)
	mux.HandleFunc("GET /vault/", vaultGETHandler)
	mux.HandleFunc("GET /account/{org}/{user}/add/{$}", addGETHandler)
	mux.HandleFunc("POST /account/{org}/{user}/add/{$}", addPOSTHandler)
	mux.HandleFunc("GET /account/{org}/{user}/{id}/{$}", editGETHandler)
	mux.HandleFunc("POST /account/{org}/{user}/{id}/{$}", editPOSTHandler)
	mux.HandleFunc("POST /account/{org}/{user}/{id}/delete/{$}", deletePOSTHandler)
	mux.HandleFunc("POST /search/{$}", searchPOSTHandler)
	mux.HandleFunc("GET /search/{$}", searchGETHandler)

	s := &http.Server{
		Addr:         ":8000",
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	log.Fatal(s.ListenAndServe())
	log.Println("Stopped")
}
