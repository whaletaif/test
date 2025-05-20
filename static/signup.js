// Firebase imports
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
  updateProfile
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import {
  getFirestore,
  doc,
  setDoc
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyDicDUXBt2tQUFM0lbaoTi0MMRWJnFFjew",
  authDomain: "data-scraping-fe855.firebaseapp.com",
  projectId: "data-scraping-fe855",
  appId: "1:188193730231:web:91f6723f8115350c946732"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
const db = getFirestore(app);

// Wait for DOM to load
window.addEventListener("DOMContentLoaded", () => {
  const loginTab = document.getElementById('loginTab');
  const signupTab = document.getElementById('signupTab');
  const nameField = document.getElementById('nameField');
  const form = document.getElementById('form');
  const googleBtn = document.querySelector('.google-btn');

  let mode = 'login'; // default mode

  loginTab.addEventListener('click', () => {
    loginTab.classList.add('active');
    signupTab.classList.remove('active');
    nameField.style.display = 'none';
    mode = 'login';
  });

  signupTab.addEventListener('click', () => {
    signupTab.classList.add('active');
    loginTab.classList.remove('active');
    nameField.style.display = 'block';
    mode = 'signup';
  });

  // Form submit (Email/Password)
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const nameInput = document.getElementById('nameField'); // Make sure this ID exists in your HTML
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (mode === 'signup') {
      createUserWithEmailAndPassword(auth, email, password)
        .then(async (userCredential) => {
          const user = userCredential.user;

          // Save the displayName to Firebase Authentication
          await updateProfile(user, { displayName: nameInput.value });
          
          // Save user info to Firestore
          await setDoc(doc(db, "users", user.uid), {
            displayName: nameInput.value,
            email: user.email
          });
          
          alert("تم إنشاء الحساب بنجاح!");
          const successMessage = document.getElementById('successMessage');
          successMessage.style.display = 'block';
          window.location.href = '/';
        })
        .catch(err => alert(err.message));
    } else {
      signInWithEmailAndPassword(auth, email, password)
        .then(() => window.location.href = '/')
        .catch(err => alert(err.message));
    }
  });

  // Google Sign-In
  googleBtn.addEventListener('click', () => {
    signInWithPopup(auth, provider)
      .then(async (result) => {
        const user = result.user;

        // Save Google user info to Firestore
        await setDoc(doc(db, "users", user.uid), {
          displayName: user.displayName,
          email: user.email
        });

        window.location.href = '/';
      })
      .catch(err => alert(err.message));
  });
});