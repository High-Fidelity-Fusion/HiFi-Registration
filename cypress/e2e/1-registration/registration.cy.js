/// <reference types="cypress" />


// Welcome to Cypress!
//
// This spec file contains a variety of sample tests
// for a todo list app that are designed to demonstrate
// the power of writing tests in Cypress.
//
// To learn more about how Cypress works and
// what makes it such an awesome testing tool,
// please read our getting started guide:
// https://on.cypress.io/introduction-to-cypress

describe('Registration Flow', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('works', () => {
    const username = "cy_test_" + Date.now().toFixed() + "@thena.gay"
    cy.contains('Event #1').should('have.length', 1).click()
    cy.contains('Create one!').click()
    cy.get('input[name=email]').type(username)
    cy.get('input[name=password1]').type("12345678!Aa")
    cy.get('input[name=password2]').type("12345678!Aa")
    cy.get('input[name=first_name]').type("Thena")
    cy.get('input[name=last_name]').type("The Tech Witch")
    cy.get('button[name=submit]').click()
    cy.contains('Event #1').should('have.length', 1).click()
    cy.contains('Thena').should('be.visible')
    // cy.get('input[name=username]').type(username)
    // cy.get('input[name=password]').type("12345678!Aa")
    // cy.get('button').contains('Login').click()
    
    cy.contains('Begin Registration').click()
    cy.get('input[name=agrees_to_policy]').should('be.visible').click()
    cy.get('button[name=submit]').click()

    cy.get('select[name=volunteer_form-wants_to_volunteer').select('False')
    cy.get('button[name=next_button]').click()

    cy.contains('Cypress Test Product Single').click()
    cy.get('.product-card.claimed').should('have.length', 1)
    cy.contains('Cypress Test Product Multi')
      .parent().find('select.quantity-input').first().select('2')
    cy.get('.product-card.claimed').should('have.length', 2)
    cy.contains('AP Please').click()

    cy.contains('Min $30').should('be.visible')
    cy.get('svg[data-icon=caret-left').click()
    cy.get('button[name=ready_to_pay]').click()

    cy.get('#order-total').should('have.text', '$35.00')
    cy.get('#checkbox').click()
    cy.get('#ppm-dropdown').select('2')
    cy.contains('Due today: $17.50').should('be.visible')
    cy.get('button').contains('Back to Selection').click()

    cy.contains('Cypress Test Product Multi')
      .parent().find('select.quantity-input').first().select('0')
    cy.get('.product-card.claimed').should('have.length', 1)
    cy.get('a').contains('Next').click()

    cy.get('#donation_input').type('1.11')
    cy.get('button[name=next]').click()

    cy.get('#order-total').should('have.text', '$21.11')
    cy.get('button').contains('Back to Selection').click()

    cy.contains('AP Please').click()
    cy.contains('Min $0').should('be.visible')
    cy.get('svg[data-icon=caret-left').click().click().click().click()
    cy.get('button[name=ready_to_pay]').click()

    cy.get('button[name=Submit]').click()

    cy.contains('Order Complete!').should('be.visible')
    cy.get('button').contains('Home').click()

    cy.contains('Cypress Test Product Single').should('be.visible')
  })
})
