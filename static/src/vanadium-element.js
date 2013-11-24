/*
 =====================================================================
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:

 1. Redistributions of source code must retain the above
 copyright notice, this list of conditions and the following
 disclaimer.

 2. Redistributions in binary form must reproduce the above
 copyright notice, this list of conditions and the following
 disclaimer in the documentation and/or other materials provided
 with the distribution.

 3. The name of the author may not be used to endorse or promote
 products derived from this software without specific prior
 written permission.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
 OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 @author Daniel Kwiecinski <daniel.kwiecinski@lambder.com>
 @copyright 2009 Daniel Kwiecinski.
 @end
 =====================================================================
 */
ElementValidation = function(element) {
  this.initialize(element)
};
ElementValidation.prototype = {

  initialize: function(element) {
    this.virgin = true;
    this.element = element;
    this.validations = [];
    this.only_on_blur = false;
    this.only_on_submit = false;
    this.wait = 100;
    this.created_advices = [];
    this.decorated = false;
    this.containers = null;
    this.invalid = undefined;
    this.advice_id = undefined; //this is general common advice for all validation instances having no specific advice defined
  },

  add_validation_instance: function(validator_type, param, advice_id) {
    this.validations.push(new Validation(this.element, validator_type, param, advice_id));
  },
  add_validation_modifier: function(modifier, param) {
    if (modifier == 'only_on_blur') {
      //  whether you want it to validate as you type or only on blur  (DEFAULT: false)
      this.only_on_blur = true
    } else if (modifier == 'only_on_submit') {
      //  whether should be validated only when the form it belongs to is submitted (DEFAULT: false)
      this.only_on_submit = true
    } else if (modifier == 'wait') {
      //  the time you want it to pause from the last keystroke before it validates (ms) (DEFAULT: 0)
      var milisesonds = parseInt(param);
      if (milisesonds != NaN && typeof(milisesonds) === "number") {
        this.wait = milisesonds;
      }
      ;
    } else if (modifier == 'advice') {
      var advice = document.getElementById(param);
      if (advice) {
        this.advice_id = param;
      }
    }
    ;
  },
  element_containers: function() {
    if (this.containers === null) {
      this.containers = new HashMap();
      var parent = this.element.parentNode;
      //search up the DOM tree
      while (parent != document) {
        var container = Vanadium.containers.get(parent);
        if (container) {
          container.add_element(this);
          this.containers.put(parent, container);
        }
        ;
        parent = parent.parentNode;
      }
      ;
    }
    ;
    return this.containers;
  },
  // context - the contect in which decoration_callback should be invoked
  // decoration_callback - the decoration used by asynchronous validation
  validate: function(decoration_context, decoration_callback) {
    var result = [];
    Vanadium.each(this.validations, function() {
      result.push(this.validate(decoration_context, decoration_callback));
    });
    return result;
  },
  decorate: function(element_validation_results, do_not_reset) {
    if (!do_not_reset) {
      this.reset();
    }
    this.decorated = true;
    var self = this;
    var passed_and_failed = Vanadium.partition(element_validation_results, function(validation_result) {
      return validation_result.success
    });
    var passed = passed_and_failed[0];
    var failed = passed_and_failed[1];
    // add apropirate CSS class to the validated element
    if (failed.length > 0) {
      this.invalid = true; //mark this validation element as invalid
      Vanadium.addValidationClass(this.element, false);
    } else if (passed.length > 0 && !this.invalid) { //when valid result comes but the previous was invalid and no reset was done, the invalid flag should stay unchanged
      this.invalid = false; //mark this validation element as valid
      Vanadium.addValidationClass(this.element, true);
    } else {
      this.invalid = undefined; //mark this validation element as undefined
    }
    ;
    // add apropirate CSS class to the validated element's containers
    this.element_containers().each(function(_element, container) {
      container.decorate();
    });
    //
    Vanadium.each(failed, function(_idx, validation_result) {
      var advice = undefined;
      if (self.advice_id) {
        advice = document.getElementById(self.advice_id);
      }
      if (advice || validation_result.advice_id) {
        advice = advice || document.getElementById(validation_result.advice_id);
        if (advice) {
          jQuery(advice).addClass(Vanadium.config.advice_class);
          var advice_is_empty = advice.childNodes.length == 0
          if (advice_is_empty || jQuery(advice).hasClass(Vanadium.empty_advice_marker_class)) {
            jQuery(advice).addClass(Vanadium.empty_advice_marker_class);
            jQuery(advice).append("<span>" + validation_result.message + "</span>");
          }
          ;
          jQuery(advice).show();
        } else {
          advice = self.create_advice(validation_result);
        }
        ;
      } else {
        advice = self.create_advice(validation_result);
      }
      ;
      Vanadium.addValidationClass(advice, false);
    });
  },
  validateAndDecorate : function(regard_virginity) {
    //That's tricky one ;)
    // 1. we are runing validate to get all validation results
    // 2. there could be possible some validations running asynchronous
    // so we won't get the result imediately. In that case the provided decoration callback
    // will be invoked on return from asynchronous callback
    // It is used by Ajax based server-side validation
    if(!regard_virginity || !this.virgin)
      this.decorate(this.validate(this, this.decorate));
  },
  create_advice: function(validation_result) {
    var span = document.createElement("span");
    this.created_advices.push(span);
    jQuery(span).addClass(Vanadium.config.advice_class);
    jQuery(span).html(validation_result.message);
    jQuery(this.element).after(span);
    return span;
  },
  reset: function() {
    this.invalid = undefined; //mark this validation element as undefined
    //    this.element_containers().each(function(_element, container) {
    //      container.decorate();
    //    });
    var element_advice = document.getElementById(this.advice_id);
    if (element_advice) {
      if (jQuery(element_advice).hasClass(Vanadium.empty_advice_marker_class)) {
        jQuery(element_advice).empty();
      }
      jQuery(element_advice).hide();
    }
    Vanadium.each(this.validations, function() {
      var advice = document.getElementById(this.adviceId);
      if (advice) {
        if (jQuery(advice).hasClass(Vanadium.empty_advice_marker_class)) {
          jQuery(advice).empty();
        }
        jQuery(advice).hide();
      }
      ;
    });

    var created_advice = this.created_advices.pop();
    while (!(created_advice === undefined)) {
      jQuery(created_advice).remove();
      created_advice = this.created_advices.pop();
    }
    ;
    Vanadium.removeValidationClass(this.element);
  },
  //
  //
  //
  /**
   * makes the validation wait the alotted time from the last keystroke
   */
  deferValidation: function() {
    if (this.wait >= 300) this.reset();
    var self = this;
    if (self.timeout) clearTimeout(self.timeout);
    self.timeout = setTimeout(function() {
      jQuery(self.element).trigger('validate');
    }, self.wait);
  },
  deferReset: function() {
    var self = this;
    if (self.reset_timeout) clearTimeout(self.reset_timeout);
    self.reset_timeout = setTimeout(function() {
      self.reset();
    }, Vanadium.config.reset_defer_timeout);
  },
  setup: function() {
    var self = this;
    this.elementType = Vanadium.getElementType(this.element);

    this.form = this.element.form;

    this.element_containers();

    if (!this.only_on_submit) {
      this.observe();
      jQuery(self.element).bind('validate', function() {
        self.validateAndDecorate.call(self, true)
      });
      jQuery(self.element).bind('defer_validation', function() {
        self.deferValidation.call(self)
      });
      jQuery(self.element).bind('reset', function() {
        self.reset.call(self)
      });
    }

  },
  observe: function() {
    var element = this.element;
    var elementType = Vanadium.getElementType(element);
    var self = this;
    jQuery(element).focus(function() {
      self.virgin = false;
    });
    switch (elementType) {
      case Vanadium.CHECKBOX:
        jQuery(element).click(function() {
          //TODO check db click !!!
          self.virgin = false; //this is here 'cos safari do not focus on checkboxes
          jQuery(self.element).trigger('validate');
        });
        break;
      //TODO check if checkboxes support on-change too. and if yes handle it!
      // let it run into the next to add a change event too
      case Vanadium.SELECT:
      case Vanadium.FILE:
        jQuery(element).change(function() {
          jQuery(element).trigger('validate');
        });
        break;
      default:
        jQuery(element).keydown(function(e) {
          if (e.keyCode != 9) {//no tabulation as it changes focus
            jQuery(element).trigger('reset');
          }
          ;
        });

        if (!this.only_on_blur) {
          jQuery(element).keyup(function(e) {
            if (e.keyCode != 9) {//no tabulation as it changes focus
              jQuery(element).trigger('defer_validation');
            }
            ;
          });
        };
        jQuery(element).blur(function() {
          jQuery(element).trigger('validate');
        });
    }
  }
};