from django.db import models

# Create your models here.
class Organization(models.Model):
    """ Organiation or company of the user.
    Every user is associated with organization/company
    th models have basic details of the company.
    """
    
    # code = 'Id'
    # company_name = 'CompanyName'
    # email = 'Email'['Address']

    code = models.CharField(max_length=10, null=True, blank=True,unique=True)
    company_name = models.CharField(max_length=254, null=False,blank=False, unique=True)
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True, db_index=True)
    # phone_number = models.CharField(max_length=15, null=True,blank=True, unique=True, db_index=True)
    # industry = models.CharField(max_length=255, null=True, blank=True)
    # annual_turnover = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organization'
        ordering = ['-created_on']

    def __str__(self):
        return self.company_name


# Create your models here.
class Customers(models.Model):
    """ Customer or company of the user.
    Every user is associated with organization/company
    th models have basic details of the company.
    """

    customer_id = models.CharField(max_length=10, null=False, blank=False,unique=True)
    company_name = models.CharField(max_length=254, null=False,blank=False, unique=False)
    display_name = models.CharField(max_length=254, null=False,blank=False, unique=False)
    email = models.EmailField(max_length=255, null=True, blank=True, unique=False)
    company_code = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='org', default=None)
 
    # phone_number = models.CharField(max_length=15, null=True,blank=True, unique=True, db_index=True)
    # industry = models.CharField(max_length=255, null=True, blank=True)
    # annual_turnover = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_on']

    def __str__(self):
        return self.display_name
